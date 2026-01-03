"""
visualize_training.py

Eğitim sürecini görselleştirir (loss, accuracy curves).
Epoch sonuçlarını okuyup grafikler oluşturur.

Kullanım:
  python visualize_training.py --logdir runs/resnet50
"""

import argparse
import torch
import matplotlib.pyplot as plt
import os
import glob

def load_training_history(weights_dir):
    """Load training history from saved checkpoints"""
    checkpoint_files = sorted(glob.glob(os.path.join(weights_dir, 'epoch_*.pth')))
    
    if not checkpoint_files:
        print("❌ No epoch checkpoints found!")
        return None
    
    history = {
        'epoch': [],
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': []
    }
    
    print(f"Found {len(checkpoint_files)} epoch checkpoints")
    
    for ckpt_file in checkpoint_files:
        try:
            ckpt = torch.load(ckpt_file, map_location='cpu', weights_only=False)
            epoch = ckpt.get('epoch', -1)
            
            # Try to extract metrics (if saved)
            history['epoch'].append(epoch + 1)
            history['val_loss'].append(ckpt.get('val_loss', 0))
            
            # Note: train metrics may not be saved in checkpoint
            # We'll plot what we have
            
        except Exception as e:
            print(f"Warning: Could not load {ckpt_file}: {e}")
            continue
    
    return history if history['epoch'] else None

def plot_training_curves(history, save_dir='runs/resnet50/plots'):
    """Plot training curves"""
    os.makedirs(save_dir, exist_ok=True)
    
    epochs = history['epoch']
    
    # Plot validation loss
    if history['val_loss']:
        plt.figure(figsize=(10, 6))
        plt.plot(epochs, history['val_loss'], 'b-o', linewidth=2, markersize=8, label='Validation Loss')
        plt.xlabel('Epoch', fontsize=12)
        plt.ylabel('Loss', fontsize=12)
        plt.title('Validation Loss over Epochs', fontsize=14, pad=15)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=11)
        plt.tight_layout()
        
        save_path = os.path.join(save_dir, 'val_loss.png')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f'📊 Validation loss plot saved to {save_path}')
        plt.close()
    
    print(f"\n✅ Training visualization completed!")
    print(f"📁 Plots saved to: {save_dir}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--logdir', type=str, default='runs/resnet50')
    args = parser.parse_args()
    
    weights_dir = os.path.join(args.logdir, 'weights')
    
    print(f"\n{'='*60}")
    print(f"📊 Training Visualization")
    print(f"{'='*60}\n")
    print(f"Log directory: {args.logdir}")
    
    # Load history
    history = load_training_history(weights_dir)
    
    if history is None:
        print("\n⚠️  No training history found!")
        print("💡 Tip: Make sure you have epoch_*.pth files in weights/ directory")
        return
    
    # Plot
    plot_training_curves(history, save_dir=os.path.join(args.logdir, 'plots'))
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📈 TRAINING SUMMARY")
    print(f"{'='*60}\n")
    print(f"Total epochs: {len(history['epoch'])}")
    if history['val_loss']:
        print(f"Best val loss: {min(history['val_loss']):.4f} (epoch {history['epoch'][history['val_loss'].index(min(history['val_loss']))]})")
    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    main()
