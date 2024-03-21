# 1. greta_SST_controller

This is a repository for the controller part of the automatic social skills training system.

For the customized Greta platform, please https://github.com/sagatake/greta_SST_platform.

This system only supports Windows systems.

## Step1: download models

Please download the openpose's body model and hand model from https://github.com/Hzzone/pytorch-openpose.

Then, put it in eval_pipeline/openpose_model.

## Step2: replace Google credential file

Please replace the Google credential file `sample.json` with your own credential.

If you don't have any credentials, please follow the instruction bellow: https://developers.google.com/workspace/guides/create-credentials.

## Step3: change paths

Please change the following paths to the appropriate ones.

* activate_env.bat
* `path_w` in copy_eval.py

## Step4: conda environment activation

Open the command prompt, then run `activate_env.bat`.

## Step5: run the main program

Run the main script with `python main_experiment_v2.py TASK NUM_TASK NUM_POSITIVE_FEEDBACK NUM_NEGATIVE_FEEDBACK`.

`TASK` should be replaced with one of `LISTEN`, `TELL`, `ASK`, `DECLINE`.

`NUM_TASK` should be a decimal number from 1 to 4.

`NUM_POSITIVE_FEEDBACK` and `NUM_NEGATIVE_FEEDBACK` should be 1 or 2 (it will be 1 if you omit these parameters).

# 2. ASAP integration

`main_experiment_v2_ASAP.py` is for integration of the ASAP model, a head and upper face gesture generation model.

Please visit https://xxxxx for more details.

# citation

```
@article{saga2023automatic,
  title={Automatic evaluation-feedback system for automated social skills training},
  author={Saga, Takeshi and Tanaka, Hiroki and Matsuda, Yasuhiro and Morimoto, Tsubasa and Uratani, Mitsuhiro and Okazaki, Kosuke and Fujimoto, Yuichiro and Nakamura, Satoshi},
  journal={Scientific Reports},
  volume={13},
  number={1},
  pages={6856},
  year={2023},
  publisher={Nature Publishing Group UK London}
}

@article{info:doi/10.2196/44857,
  author="Tanaka, Hiroki
  and Saga, Takeshi
  and Iwauchi, Kota
  and Honda, Masato
  and Morimoto, Tsubasa
  and Matsuda, Yasuhiro
  and Uratani, Mitsuhiro
  and Okazaki, Kosuke
  and Nakamura, Satoshi",
  title="The Validation of Automated Social Skills Training in Members of the General Population Over 4 Weeks: Comparative Study",
  journal="JMIR Form Res",
  year="2023",
  month="Apr",
  day="27",
  volume="7",
  pages="e44857",
  doi="10.2196/44857",
  url="https://formative.jmir.org/2023/1/e44857",
  url="https://doi.org/10.2196/44857",
  url="http://www.ncbi.nlm.nih.gov/pubmed/37103996"
}

@inproceedings{cao2017realtime,
  author = {Zhe Cao and Tomas Simon and Shih-En Wei and Yaser Sheikh},
  booktitle = {CVPR},
  title = {Realtime Multi-Person 2D Pose Estimation using Part Affinity Fields},
  year = {2017}
}

@inproceedings{simon2017hand,
  author = {Tomas Simon and Hanbyul Joo and Iain Matthews and Yaser Sheikh},
  booktitle = {CVPR},
  title = {Hand Keypoint Detection in Single Images using Multiview Bootstrapping},
  year = {2017}
}

@inproceedings{wei2016cpm,
  author = {Shih-En Wei and Varun Ramakrishna and Takeo Kanade and Yaser Sheikh},
  booktitle = {CVPR},
  title = {Convolutional pose machines},
  year = {2016}
}
```
