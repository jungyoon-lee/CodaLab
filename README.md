# CodaLab Submit

## Install
```
git clone https://github.com/jungyoon-lee/codalab
cd codalab
pip install -e .
```

## Usage

### submit.py
```
from codalab import CodaLab
import argparse

config = {
    'login': 'yourid',
    'password': 'yourpassword',
    'competition_id': '7680',
}

if __name__ == '__main__':
    codalab = CodaLab(config)

    parser = argparse.ArgumentParser()
    
    parser.add_argument('--filename', type=str, default='./result.zip')
    parser.add_argument('--description', type=str, default='')

    args = parser.parse_args()

    submit_dict = {
        'filename': args.filename,
        'description': args.description
    }

    codalab.submit(submit_dict)
```

### Bash Script
```
#!/bin/bash

declare -a iterations=("0059999" "0069999")

for iter in "${iterations[@]}"
do
  python train_net_vita.py --eval-only --config-file configs/youtubevis_2021/test.yaml MODEL.WEIGHTS output/model_${iter}.pth
  python submit.py --filename ./output/inference/results_${iter}.zip
done
```
