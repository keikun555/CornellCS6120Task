import csv

import click

@click.command()
@click.argument('csv_path', metavar='CSVFILE', type=click.Path(exists=True))
def main(csv_path):
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header = next(reader)
        data: dict[tuple[str, str], int] = dict()
        runs = set()
        for benchmark, run, result in reader:
            if result in ("timeout",):
                continue
            runs.add(run)
            data[(benchmark, run)] = int(result)
        print(",".join(header[:2] + ["dynamic_instances_removed"]))
        for (benchmark, run), result in sorted(data.items()):
            result = data[(benchmark, "baseline")] - result
            print(f'{benchmark},{run},{result}')

if __name__ == "__main__":
    main()
