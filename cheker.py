import torch
print("Using GPU" if torch.cuda.is_available() else "Using CPU")
import torch
print(torch.cuda.is_available())  # Should return True
