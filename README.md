# greta_SST_controller

This is a repository for the controller part of the automatic social skills training system.

For the customized Greta platform, please https://github.com/sagatake/greta_SST_platform.

Please download the openpose's body model and hand model from https://github.com/Hzzone/pytorch-openpose.
Then, put it in eval_pipeline/openpose_model.

# citation

'''
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
'''
