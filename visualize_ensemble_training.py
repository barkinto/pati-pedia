"""
Visualization Tools for Training History
Generate publication-quality plots for academic papers
"""

import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np
import os
import argparse

# Set style for academic papers
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")

def plot_training_history(history, model_name, save_dir):
    """Plot training and validation metrics"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    epochs = range(1, len(history['train_loss']) + 1)
    
    # Loss
    axes[0, 0].plot(epochs, history['train_loss'], 'b-', label='Train Loss', linewidth=2)
    axes[0, 0].plot(epochs, history['val_loss'], 'r-', label='Val Loss', linewidth=2)
    axes[0, 0].set_title(f'{model_name} - Loss', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Epoch', fontsize=12)
    axes[0, 0].set_ylabel('Loss', fontsize=12)
    axes[0, 0].legend(loc='best', fontsize=10)
    axes[0, 0].grid(True, alpha=0.3)
    
    # Top-1 Accuracy
    axes[0, 1].plot(epochs, history['train_acc'], 'b-', label='Train Acc', linewidth=2)
    axes[0, 1].plot(epochs, history['val_acc'], 'r-', label='Val Acc', linewidth=2)
    axes[0, 1].set_title(f'{model_name} - Top-1 Accuracy', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Epoch', fontsize=12)
    axes[0, 1].set_ylabel('Accuracy (%)', fontsize=12)
    axes[0, 1].legend(loc='best', fontsize=10)
    axes[0, 1].grid(True, alpha=0.3)
    
    # Top-3 Accuracy
    axes[1, 0].plot(epochs, history['train_top3'], 'b-', label='Train Top-3', linewidth=2)
    axes[1, 0].plot(epochs, history['val_top3'], 'r-', label='Val Top-3', linewidth=2)
    axes[1, 0].set_title(f'{model_name} - Top-3 Accuracy', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Epoch', fontsize=12)
    axes[1, 0].set_ylabel('Accuracy (%)', fontsize=12)
    axes[1, 0].legend(loc='best', fontsize=10)
    axes[1, 0].grid(True, alpha=0.3)
    
    # Top-5 Accuracy
    axes[1, 1].plot(epochs, history['train_top5'], 'b-', label='Train Top-5', linewidth=2)
    axes[1, 1].plot(epochs, history['val_top5'], 'r-', label='Val Top-5', linewidth=2)
    axes[1, 1].set_title(f'{model_name} - Top-5 Accuracy', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Epoch', fontsize=12)
    axes[1, 1].set_ylabel('Accuracy (%)', fontsize=12)
    axes[1, 1].legend(loc='best', fontsize=10)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    save_path = os.path.join(save_dir, f'{model_name}_training_curves.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Training curves saved: {save_path}")


def plot_learning_rate(history, model_name, save_dir):
    """Plot learning rate schedule"""
    if 'learning_rate' not in history:
        return
    
    plt.figure(figsize=(10, 6))
    epochs = range(1, len(history['learning_rate']) + 1)
    plt.plot(epochs, history['learning_rate'], 'g-', linewidth=2)
    plt.title(f'{model_name} - Learning Rate Schedule', fontsize=14, fontweight='bold')
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Learning Rate', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    
    save_path = os.path.join(save_dir, f'{model_name}_learning_rate.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Learning rate plot saved: {save_path}")


def compare_all_models(history_files, save_dir):
    """Compare training curves of all models"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for idx, (model_name, history_file) in enumerate(history_files.items()):
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        epochs = range(1, len(history['val_loss']) + 1)
        color = colors[idx % len(colors)]
        
        # Val Loss
        axes[0, 0].plot(epochs, history['val_loss'], color=color, 
                       label=model_name, linewidth=2, marker='o', markersize=3)
        
        # Val Top-1 Accuracy
        axes[0, 1].plot(epochs, history['val_acc'], color=color,
                       label=model_name, linewidth=2, marker='o', markersize=3)
        
        # Val Top-3 Accuracy
        axes[1, 0].plot(epochs, history['val_top3'], color=color,
                       label=model_name, linewidth=2, marker='o', markersize=3)
        
        # Val Top-5 Accuracy
        axes[1, 1].plot(epochs, history['val_top5'], color=color,
                       label=model_name, linewidth=2, marker='o', markersize=3)
    
    axes[0, 0].set_title('Validation Loss Comparison', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Epoch', fontsize=12)
    axes[0, 0].set_ylabel('Loss', fontsize=12)
    axes[0, 0].legend(loc='best', fontsize=10)
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].set_title('Top-1 Accuracy Comparison', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Epoch', fontsize=12)
    axes[0, 1].set_ylabel('Accuracy (%)', fontsize=12)
    axes[0, 1].legend(loc='best', fontsize=10)
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].set_title('Top-3 Accuracy Comparison', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Epoch', fontsize=12)
    axes[1, 0].set_ylabel('Accuracy (%)', fontsize=12)
    axes[1, 0].legend(loc='best', fontsize=10)
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].set_title('Top-5 Accuracy Comparison', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Epoch', fontsize=12)
    axes[1, 1].set_ylabel('Accuracy (%)', fontsize=12)
    axes[1, 1].legend(loc='best', fontsize=10)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    save_path = os.path.join(save_dir, 'all_models_comparison.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Model comparison saved: {save_path}")


def plot_metrics_summary(history_files, save_dir):
    """Create summary bar charts"""
    
    models = []
    final_train_acc = []
    final_val_acc = []
    best_val_acc = []
    final_val_top3 = []
    final_val_top5 = []
    
    for model_name, history_file in history_files.items():
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        models.append(model_name)
        final_train_acc.append(history['train_acc'][-1])
        final_val_acc.append(history['val_acc'][-1])
        best_val_acc.append(max(history['val_acc']))
        final_val_top3.append(history['val_top3'][-1])
        final_val_top5.append(history['val_top5'][-1])
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    x = np.arange(len(models))
    width = 0.35
    
    # Final vs Best accuracy
    axes[0].bar(x - width/2, final_val_acc, width, label='Final Val Acc', alpha=0.8)
    axes[0].bar(x + width/2, best_val_acc, width, label='Best Val Acc', alpha=0.8)
    axes[0].set_title('Final vs Best Validation Accuracy', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Accuracy (%)', fontsize=12)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(models, rotation=45, ha='right')
    axes[0].legend(fontsize=10)
    axes[0].grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, (v1, v2) in enumerate(zip(final_val_acc, best_val_acc)):
        axes[0].text(i - width/2, v1 + 1, f'{v1:.1f}%', ha='center', fontsize=9)
        axes[0].text(i + width/2, v2 + 1, f'{v2:.1f}%', ha='center', fontsize=9)
    
    # Top-1, Top-3, Top-5 comparison
    width = 0.25
    axes[1].bar(x - width, final_val_acc, width, label='Top-1', alpha=0.8)
    axes[1].bar(x, final_val_top3, width, label='Top-3', alpha=0.8)
    axes[1].bar(x + width, final_val_top5, width, label='Top-5', alpha=0.8)
    axes[1].set_title('Top-k Accuracy Comparison', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Accuracy (%)', fontsize=12)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(models, rotation=45, ha='right')
    axes[1].legend(fontsize=10)
    axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    save_path = os.path.join(save_dir, 'metrics_summary.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Metrics summary saved: {save_path}")


def generate_latex_training_table(history_files, save_path):
    """Generate LaTeX table with training results"""
    
    latex = r"""\begin{table}[htbp]
\centering
\caption{Training Results Summary - All Models}
\label{tab:training_results}
\begin{tabular}{lcccccc}
\hline
\textbf{Model} & \textbf{Epochs} & \textbf{Best Val} & \textbf{Final Val} & \textbf{Top-3} & \textbf{Top-5} & \textbf{Final Loss} \\
& & \textbf{Acc (\%)} & \textbf{Acc (\%)} & \textbf{Acc (\%)} & \textbf{Acc (\%)} & \\
\hline
"""
    
    for model_name, history_file in history_files.items():
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        epochs = len(history['val_acc'])
        best_val = max(history['val_acc'])
        final_val = history['val_acc'][-1]
        final_top3 = history['val_top3'][-1]
        final_top5 = history['val_top5'][-1]
        final_loss = history['val_loss'][-1]
        
        latex += f"{model_name} & {epochs} & {best_val:.2f} & {final_val:.2f} & "
        latex += f"{final_top3:.2f} & {final_top5:.2f} & {final_loss:.4f} \\\\\n"
    
    latex += r"""\hline
\end{tabular}
\end{table}
"""
    
    with open(save_path, 'w') as f:
        f.write(latex)
    
    print(f"✓ LaTeX training table saved: {save_path}")


def main():
    parser = argparse.ArgumentParser(description='Visualize Training History')
    parser.add_argument('--history-dir', default='runs/ensemble', 
                       help='Directory containing history JSON files')
    parser.add_argument('--output-dir', default='runs/ensemble/visualizations',
                       help='Output directory for plots')
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Find all history files
    history_files = {}
    for file in os.listdir(args.history_dir):
        if file.endswith('_history.json'):
            model_name = file.replace('_history.json', '')
            history_files[model_name] = os.path.join(args.history_dir, file)
    
    if not history_files:
        print("No history files found!")
        return
    
    print(f"Found {len(history_files)} models: {list(history_files.keys())}")
    
    # Plot individual model histories
    print("\nGenerating individual model plots...")
    for model_name, history_file in history_files.items():
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        plot_training_history(history, model_name, args.output_dir)
        plot_learning_rate(history, model_name, args.output_dir)
    
    # Compare all models
    print("\nGenerating comparison plots...")
    compare_all_models(history_files, args.output_dir)
    plot_metrics_summary(history_files, args.output_dir)
    
    # Generate LaTeX table
    latex_path = os.path.join(args.output_dir, 'training_results_table.tex')
    generate_latex_training_table(history_files, latex_path)
    
    print(f"\n✓ All visualizations saved to: {args.output_dir}")


if __name__ == '__main__':
    main()
