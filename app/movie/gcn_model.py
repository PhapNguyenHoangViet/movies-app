import torch
from torch.nn import functional as F
from torch_geometric.nn import GCNConv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = os.path.join(BASE_DIR, 'movie', 'gcn_model.pth')

class GCN(torch.nn.Module):
    def __init__(self, num_features, hidden_channels, num_users, num_items):
        super(GCN, self).__init__()
        # Thêm nhiều lớp convolution
        self.conv1 = GCNConv(num_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels // 2)
        self.conv3 = GCNConv(hidden_channels // 2, num_items)
        self.dropout = torch.nn.Dropout(0.5)
        
        # Embedding với regularization
        self.user_embeddings = torch.nn.Embedding(num_users, hidden_channels)
        self.item_embeddings = torch.nn.Embedding(num_items, hidden_channels)
        
    
    def forward(self, x, edge_index):
        x = F.relu((self.conv1(x, edge_index)))
        x = self.dropout(x)
        x = F.relu((self.conv2(x, edge_index)))
        x = self.dropout(x)
        x = self.conv3(x, edge_index)
        return x
    
    
    def recommend(self, user_id, k=5):
        self.eval()
        with torch.no_grad():
            user_embedding = self.user_embeddings(torch.tensor([user_id], dtype=torch.long))
            item_embeddings = self.item_embeddings.weight
            item_scores = torch.matmul(user_embedding, item_embeddings.t())
            _, sorted_indices = torch.topk(item_scores, k)
            return sorted_indices.squeeze().tolist()


def load_model():
    num_features = 50
    hidden_channels = 64
    num_users = 943
    num_items = 1682

    model = GCN(num_features, hidden_channels, num_users, num_items)
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    model.load_state_dict(torch.load(MODEL_PATH))
    model.eval()
    return model

def recommend_movies(user_id=1, k=5):
    model = load_model()
    recommended_item_ids = model.recommend(user_id, k)
    return recommended_item_ids