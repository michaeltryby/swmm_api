if 0:
    try:
        from tqdm import tqdm as custom_iter
    except ImportError as e:
        def custom_iter(i, desc=None):
            return i

else:
    def custom_iter(i, desc=None):
        return i