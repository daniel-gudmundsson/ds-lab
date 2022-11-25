import os
from typing import Tuple
import random

import pandas as pd
from PIL import Image
from torch import Tensor
from torch.utils.data import Dataset, WeightedRandomSampler
from torchvision.transforms import (
    ToTensor,
    Normalize,
    RandomHorizontalFlip,
    RandomVerticalFlip,
)
import torch
from torchvision.models import ResNet50_Weights


class SurvivalDataset(Dataset):
    def __init__(
        self,
        df: pd.DataFrame,
        patient_slide_map_path: str,
        transform=ResNet50_Weights.DEFAULT.transforms(),
        augmentation=True,
    ) -> None:
        self.event_indicator = df["vital_status"].to_numpy()
        self.days_to_event = df["days_to_event"].to_numpy()
        self.patient_ids = df["ID"].to_numpy()
        with open(patient_slide_map_path, "rb") as f:
            self.patient_slide_map = pickle.load(f)

        self.transform = transform

        if augmentation:
            self.augmentation = torch.nn.Sequential(
                RandomVerticalFlip(0.5), RandomHorizontalFlip(0.5)
            )
        else:
            self.augmentation = None

    def __len__(self):
        return len(self.img_paths)

    def __getitem__(self, idx) -> Tuple[Tensor, Tensor, Tensor]:

        patient_id = self.patient_ids[idx]

        img_path = random.choice(self.patient_slide_map[patient_id])

        image = Image.open(img_path)
        image = ToTensor()(image)
        assert image.shape == torch.Size([3, 1500, 1500])
        if self.transform:
            image = self.transform(image)

        if self.augmentation:
            image = self.augmentation(image)

        event_indicator = torch.tensor(self.event_indicator[idx])
        days_to_event = torch.tensor(self.days_to_event[idx])

        return image, event_indicator, days_to_event


# Example usage
if __name__ == "__main__":
    import pickle
    import os

    import pandas as pd

    with open("data/TCGA_y_train.pkl", "rb") as f:
        train_df = pickle.load(f)

    dataset = SurvivalDataset(train_df, "data/TCGA_patient_slide_map.pkl")
