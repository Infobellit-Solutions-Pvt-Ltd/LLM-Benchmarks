import click
import yaml
from pathlib import Path
from echoswift.llm_inference_benchmark import EchoSwift
from echoswift.dataset import download_dataset_files
from echoswift.utils.plot_results import plot_benchmark_results 
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    EchoSwift: LLM Inference Benchmarking Tool

    \b
    Usage:
    1. Create a config.yaml file (see README for configuration details)
    2. Run 'echoswift dataprep' to download the dataset
    3. Run 'echoswift start --config config.yaml' to start the benchmark
    4. Run 'echoswift plot --results-dir benchmark_results' to generate plots

    For more detailed information, visit:
    https://github.com/Infobellit-Solutions-Pvt-Ltd/EchoSwift/blob/main/README.md
    """
    pass

@cli.command()
@click.option('--config', required=True, type=click.Path(exists=True), help='Path to the configuration file')
def start(config):
    """Start the EchoSwift benchmark using the specified config file"""
    config_path = Path(config)
    cfg = load_config(config_path)
    
    dataset_dir = Path("Input_Dataset")
    if not dataset_dir.exists() or not any(dataset_dir.iterdir()):
        logging.error("Filtered dataset not found. Please run 'echoswift dataprep' before starting the benchmark.")
        raise click.Abort()

    logging.info("Using Filtered_ShareGPT_Dataset for the benchmark.")
    
    benchmark = EchoSwift(
        output_dir=cfg['out_dir'],
        api_url=cfg['base_url'],
        provider=cfg['provider'],
        model_name=cfg.get('model'),
        max_requests=cfg['max_requests'],
        user_counts=cfg['user_counts'],
        input_tokens=cfg['input_tokens'],
        output_tokens=cfg['output_tokens'],
        dataset_dir=str(dataset_dir)
    )
    
    benchmark.run_benchmark()

@cli.command()
def dataprep():
    """Download the filtered ShareGPT dataset"""
    download_dataset_files("sarthakdwi/EchoSwift-8k")

@cli.command()
@click.option('--results-dir', required=True, type=click.Path(exists=True), help='Directory containing benchmark results')
def plot(results_dir):
    """Plot graphs using benchmark results"""
    results_path = Path(results_dir)
    if not results_path.is_dir():
        raise click.BadParameter("The specified results directory is not a directory.")
    
    try:
        plot_benchmark_results(results_path)
        click.echo(f"Plots have been generated and saved in {results_path}")
    except Exception as e:
        click.echo(f"An error occurred while plotting results: {e}", err=True)

if __name__ == '__main__':
    cli()