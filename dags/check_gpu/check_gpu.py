import os


def check_gpu():
    if os.system('nvidia-smi') == 0:
        print('GPU is available')
    else:
        print('GPU is not available')


if __name__ == '__main__':
    check_gpu()
