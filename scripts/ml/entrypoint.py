from experiment import ToxicityPredictionExperiment
from options import parse_args


def main() -> None:
    cfg = parse_args()
    experiment = ToxicityPredictionExperiment(cfg=cfg)
    experiment.prepare_dataset()
    experiment.run_trainings()


if __name__ == "__main__":
    main()
