# train and test CartoonGAN

from CartoonGAN_model import Generator, Discriminator, FeatureExtractor
from CartoonGAN_train import CartoonGANTrainer
from config import Config
from dataloader import load_image_dataloader

import torch
import matplotlib.pyplot as plt
import argparse
import torchvision.utils as tvutils


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--test',
                        action='store_true',
                        help='Use this argument to test generator and compute FID score')

    parser.add_argument('--model_path',
                        help='Path to saved model')

    parser.add_argument('--test_image_path',
                        default=Config.test_photo_image_dir,
                        help='Path to test photo images')

    args = parser.parse_args()

    return args


def load_model(generator, discriminator, checkpoint_path):
    checkpoint = torch.load(checkpoint_path)
    generator.load_state_dict(checkpoint['generator_state_dict'])
    discriminator.load_state_dict(checkpoint['discriminator_state_dict'])


def generate_and_save_images(generator, test_image_loader, save_path):
    # TODO
    # for each image in test_image_loader, generate image and save
    generator.eval()
    pass


def main():

    args = get_args()

    device = Config.device
    print("PyTorch running with device {0}".format(device))

    print("Creating models...")
    generator = Generator().to(device)
    discriminator = Discriminator().to(device)
    feature_extractor = FeatureExtractor().to(device)

    if args.test:
        assert args.model_path, 'model_path must be provided for testing'
        print('Testing...')
        generator.eval()

        print('Loading models')
        load_model(generator, discriminator, args.model_path)
        # Do testing stuff
        # ex. generate image, compute fid score

        test_images = load_image_dataloader(root_dir=args.test_image_path, batch_size=Config.device * 2, shuffle=False)

        image_batch = next(iter(test_images))
        new_images = generator(image_batch)

        tvutils.save_image(image_batch, 'test_images.jpg', nrow=4, padding=2, normalize=True, range=(-1, 1))
        tvutils.save_image(new_images, 'generated_images.jpg', nrow=4, padding=2, normalize=True, range=(-1, 1))

        # TODO
        # Compute FID score

    else:
        print("Training...")

        # load dataloaders
        photo_images = load_image_dataloader(root_dir=Config.photo_image_dir)
        animation_images = load_image_dataloader(root_dir=Config.animation_image_dir)
        edge_smoothed_images = load_image_dataloader(root_dir=Config.edge_smoothed_image_dir)

        print("Loading Trainer...")
        trainer = CartoonGANTrainer(generator, discriminator, feature_extractor, photo_images, animation_images,
                                    edge_smoothed_images)
        if args.model_path:
            trainer.load_checkpoint(args.model_path)

        print('Start Training...')
        loss_D_hist, loss_G_hist, loss_content_hist = trainer.train(num_epochs=Config.num_epochs,
                                                                    initialization_epochs=Config.initialization_epochs)

        plt.plot(loss_D_hist, label='Discriminator loss')
        plt.plot(loss_G_hist, label='Generator loss')
        plt.plot(loss_content_hist, label='Content loss')
        plt.legend()
        plt.savefig('CartoonGAN_train_history.jpg')
        plt.show()


if __name__ == '__main__':
    main()



