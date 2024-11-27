import os
import torch
import torch.nn.functional as F
import torch.optim as optim
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

class MovieRecommender:
    def __init__(self, 
                 model_path=None, 
                 num_features=50, 
                 hidden_channels=64, 
                 num_users=943, 
                 num_items=1682):

        self.num_features = num_features
        self.hidden_channels = hidden_channels
        self.num_users = num_users
        self.num_items = num_items
        
        self.model = self._create_gcn_model()
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def _create_gcn_model(self):
        return GCNMovieRecommender(
            num_features=self.num_features, 
            hidden_channels=self.hidden_channels, 
            num_users=self.num_users, 
            num_items=self.num_items
        )
    
    def load_model(self, model_path):
        try:
            self.model.load_state_dict(torch.load(model_path))
            self.model.eval()
            print(f"Loaded model from {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def save_model(self, model_path):
        try:
            torch.save(self.model.state_dict(), model_path)
            print(f"Model saved to {model_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def recommend_movies(self, user_id, k=5):
        try:
            recommended_item_ids = self.model.recommend(user_id, k)
            return recommended_item_ids
        except Exception as e:
            print(f"Recommendation error: {e}")
            return []
    
    def update_model(self, 
                     ratings_data, 
                     feature_matrix, 
                     epochs=10, 
                     learning_rate=0.0005, 
                     weight_decay=1e-5):
        try:
            rate_train_val, rate_test = train_test_split(ratings_data, test_size=0.2, random_state=1)
            rate_train, rate_val = train_test_split(rate_train_val, test_size=0.2, random_state=1)
            
            # Chuẩn bị dữ liệu graph
            train_data = self._create_interaction_graph(rate_train, feature_matrix)
            train_loader = DataLoader([train_data], batch_size=1)
            
            # Chuẩn bị optimizer và loss
            optimizer = optim.AdamW(
                self.model.parameters(), 
                lr=learning_rate, 
                weight_decay=weight_decay
            )
            criterion = torch.nn.MSELoss()
            
            # Training loop
            self.model.train()
            for epoch in range(epochs):
                total_loss = 0
                for data in train_loader:
                    optimizer.zero_grad()
                    out = self.model(data.x, data.edge_index)
                    edge_scores = (out[data.edge_index[0]] * out[data.edge_index[1]]).sum(dim=1)
                    loss = torch.sqrt(criterion(edge_scores, data.edge_attr.to(torch.float)))
                    loss.backward()
                    optimizer.step()
                    total_loss += loss.item()
                
                train_loss = total_loss / len(train_loader)
                if (epoch + 1) % 2 == 0:
                    print(f'Epoch {epoch + 1}, Train Loss: {train_loss:.4f}')
            
            self.model.eval()
            return train_loss
        
        except Exception as e:
            print(f"Model update error: {e}")
            return None
    
    def _create_interaction_graph(self, ratings, features):
        user_ids = ratings['user_id'].values
        item_ids = ratings['movie_id'].values + self.num_users
        ratings_values = ratings['rating'].values
                
        edge_index = torch.tensor([
            np.concatenate([user_ids, item_ids]),
            np.concatenate([item_ids, user_ids])
        ], dtype=torch.long)
        
        edge_attr = torch.tensor(
            np.concatenate([ratings_values, ratings_values]), 
            dtype=torch.float
        )
        
        graph_data = Data(
            x=features, 
            edge_index=edge_index, 
            edge_attr=edge_attr
        )
        
        return graph_data


class GCNMovieRecommender(torch.nn.Module):
    def __init__(self, num_features, hidden_channels, num_users, num_items):
        super().__init__()
        self.conv1 = GCNConv(num_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels // 2)
        self.conv3 = GCNConv(hidden_channels // 2, num_items)
        self.dropout = torch.nn.Dropout(0.5)
        
        self.user_embeddings = torch.nn.Embedding(num_users, hidden_channels)
        self.item_embeddings = torch.nn.Embedding(num_items, hidden_channels)
    
    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        x = self.dropout(x)
        x = F.relu(self.conv2(x, edge_index))
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

       
from django.db import connection
import pandas as pd

def fetch_data_as_dataframe(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return pd.DataFrame(cursor.fetchall(), columns=columns)

# Truy vấn SQL
query_movies = "SELECT movie_id, movie_title, release_date, overview, runtime, keywords, director,caster FROM core_movie"
query_ratings = "SELECT user_id, movie_id, rating, timestamp FROM core_rating"
query_users = "SELECT user_id, age, sex, occupation FROM core_user"

df_movies = fetch_data_as_dataframe(query_movies)
df_ratings = fetch_data_as_dataframe(query_ratings)
df_users = fetch_data_as_dataframe(query_users)

print(df_movies.head())
print(df_ratings.head())
print(df_users.head())