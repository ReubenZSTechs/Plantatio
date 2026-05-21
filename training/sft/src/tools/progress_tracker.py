from tqdm import tqdm

class ProgressTracker:
    def __init__(self):
        self.pbar = None
        self.total = 0
        self.current = 0

    def init(self, total):
        self.total = total
        self.pbar = tqdm(total=total, desc="Dataset Generation")

    def step(self, label=""):
        self.current += 1
        self.pbar.update(1)
        if label:
            self.pbar.set_postfix_str(label)

    def close(self):
        self.pbar.close()