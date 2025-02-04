"""
Written by Jason Taylor <jasonrbtaylor@gmail.com> 2018-2019
"""

import json
import os

import torch

import data
import model
import train
from vis import generate_between_classes

def run(dataset='mnist', 
        batch_size=64, 
        n_features=200, 
        n_layers=6, 
        n_bins=4,
        optimizer='adam', 
        learnrate=1e-4, 
        dropout=0.9, 
        exp_name='pixelCNN',
        exp_dir='~/experiments/conditional-pixelcnn/', 
        cuda=True,
        resume=False):

    exp_name += '_%s_%ifeat_%ilayers_%ibins'%(
        dataset, n_features, n_layers, n_bins)
    exp_dir = os.path.join(os.path.expanduser(exp_dir), exp_name)
    if not os.path.isdir(exp_dir):
        os.makedirs(exp_dir)

    # Data loaders
    train_loader, val_loader, onehot_fcn, n_classes = data.loader(dataset,
                                                                  batch_size)

    if not resume:
        # Store experiment params in params.json
        params = {'batch_size':batch_size, 'n_features':n_features,
                  'n_layers':n_layers, 'n_bins':n_bins, 'optimizer': optimizer,
                  'learnrate':learnrate, 'dropout':dropout, 'cuda':cuda}
        with open(os.path.join(exp_dir,'params.json'),'w') as f:
            json.dump(params,f)

        # Model
        net = model.PixelCNN(1, n_classes, n_features, 
                             n_layers, n_bins, dropout)
        
    else:
        # if resuming, need to have params, stats and checkpoint files
        if not (os.path.isfile(os.path.join(exp_dir,'params.json'))
                and os.path.isfile(os.path.join(exp_dir,'stats.json'))
                and os.path.isfile(os.path.join(exp_dir,'last_checkpoint'))):
            raise Exception('Missing param, stats or checkpoint file on resume')
        net = torch.load(os.path.join(exp_dir, 'last_checkpoint'))

    print(net)
    # Define loss fcn, incl. label formatting from input
    def input2label(x):
        return torch.squeeze(torch.round((n_bins-1)*x).type(torch.LongTensor),1)
    loss_fcn = torch.nn.NLLLoss2d()

    # Train
    train.fit(train_loader, val_loader, net, exp_dir, input2label, loss_fcn,
              onehot_fcn, n_classes, optimizer, learnrate=learnrate, cuda=cuda,
              resume=resume)

    # Generate some between-class examples
    generate_between_classes(net, [28, 28], [1, 7],
                             os.path.join(exp_dir,'1-7.jpeg'), n_classes, cuda)
    generate_between_classes(net, [28, 28], [3, 8],
                             os.path.join(exp_dir,'3-8.jpeg'), n_classes, cuda)
    generate_between_classes(net, [28, 28], [4, 9],
                             os.path.join(exp_dir,'4-9.jpeg'), n_classes, cuda)
    generate_between_classes(net, [28, 28], [5, 6],
                             os.path.join(exp_dir,'5-6.jpeg'), n_classes, cuda)


if __name__ == "__main__":
    run(n_features=300, n_layers=8, learnrate=3e-4, dropout=0.7)
