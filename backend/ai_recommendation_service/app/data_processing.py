import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import torch

class PriceDataset(torch.utils.data.Dataset):
    def __init__(self, data, sequence_length):
        self.data = data
        self.sequence_length = sequence_length
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))

    def __len__(self):
        return len(self.scaled_data) - self.sequence_length

    def __getitem__(self, idx):
        x = self.scaled_data[idx:idx + self.sequence_length]
        y = self.scaled_data[idx + self.sequence_length]
        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

def preprocess_data(df: pd.DataFrame, target_column: str, sequence_length: int):
    data = df[target_column].values
    dataset = PriceDataset(data, sequence_length)
    return dataset, dataset.scaler

def inverse_transform_data(scaler, scaled_data):
    return scaler.inverse_transform(scaled_data) 