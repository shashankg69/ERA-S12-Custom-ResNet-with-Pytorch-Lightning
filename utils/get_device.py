import torch
import torchinfo
from torch_lr_finder import LRFinder
from matplotlib import pyplot as plt
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

SEED = 42
DEVICE = None


def get_device():
    global DEVICE
    if DEVICE is not None:
        return DEVICE

    if torch.cuda.is_available():
        DEVICE = "cuda"
    elif torch.backends.mps.is_available():
        DEVICE = "mps"
    else:
        DEVICE = "cpu"
    print("Device Selected:", DEVICE)
    return DEVICE


def set_seed(seed=SEED):
    torch.manual_seed(seed)
    if get_device() == 'cuda':
        torch.cuda.manual_seed(seed)


def plot_examples(images, labels, figsize=None, n=20):
    _ = plt.figure(figsize=figsize)

    for i in range(n):
        plt.subplot(4, n//4, i + 1)
        plt.tight_layout()
        image = images[i]
        plt.imshow(image, cmap='gray')
        label = labels[i]
        plt.title(str(label))
        plt.xticks([])
        plt.yticks([])


def find_lr(model, data_loader, optimizer, criterion):
    lr_finder = LRFinder(model, optimizer, criterion)
    lr_finder.range_test(data_loader, end_lr=0.1, num_iter=100, step_mode='exp')
    _, best_lr = lr_finder.plot()
    lr_finder.reset()
    return best_lr


def get_incorrect_preds(prediction, labels):
    prediction = prediction.argmax(dim=1)
    indices = prediction.ne(labels).nonzero().reshape(-1).tolist()
    return indices, prediction[indices].tolist(), labels[indices].tolist()


def get_cam_visualisation(model, dataset, input_tensor, label, target_layer, use_cuda=False):
    grad_cam = GradCAM(model=model, target_layers=[target_layer], use_cuda=use_cuda)

    targets = [ClassifierOutputTarget(label)]

    grayscale_cam = grad_cam(input_tensor=input_tensor.unsqueeze(0), targets=targets)
    grayscale_cam = grayscale_cam[0, :]

    output = show_cam_on_image(dataset.show_transform(input_tensor).cpu().numpy(), grayscale_cam,
                               use_rgb=True)
    return output


def model_summary(model, input_size=None):
    return torchinfo.summary(model, input_size=input_size, depth=5,
                             col_names=["input_size", "output_size", "num_params", "params_percent"])