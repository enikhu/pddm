# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import tensorflow as tf
import os
import pickle
from pddm.utils.helper_funcs import plot_mean_std


class Saver:

    def __init__(self, save_dir, sess):

        ### init vars
        self.iter_num = -7
        self.save_dir = save_dir
        self.sess = sess

        ### make directories for saving data
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            os.makedirs(self.save_dir + '/losses')
            os.makedirs(self.save_dir + '/models')
            os.makedirs(self.save_dir + '/saved_rollouts')
            os.makedirs(self.save_dir + '/training_data')

        ### tensorflow saver
        self.tf_saver = tf.train.Saver(max_to_keep=0)

    def save_initialData(self, params, rollouts_trainRand, rollouts_valRand):

        pickle.dump(
            rollouts_trainRand,
            open(self.save_dir + '/training_data/train_rollouts_rand.pickle', 'wb'),
            pickle.HIGHEST_PROTOCOL)
        pickle.dump(
            rollouts_valRand,
            open(self.save_dir + '/training_data/val_rollouts_rand.pickle',
                 'wb'), pickle.HIGHEST_PROTOCOL)
        pickle.dump(params, open(self.save_dir + '/params.pkl', 'wb'),
                    pickle.HIGHEST_PROTOCOL)

    def save_model(self):

        if self.iter_num==-7:
            print("Error: MUST SPECIFY ITER_NUM FOR SAVER...")
            import IPython
            IPython.embed()

        # save the model under current iteration number
        # but also update the finalModel.ckpt too
        if self.iter_num%50 == 0:
            save_path1 = self.tf_saver.save(
                self.sess, self.save_dir + '/models/model_aggIter' + str(
                    self.iter_num) + '.ckpt')
        save_path2 = self.tf_saver.save(
            self.sess, self.save_dir + '/models/finalModel.ckpt')
        print("Model saved at ", save_path2)

    ############################################################################################
    ##### The following 2 saves together represent a single "iteration"
    ########## (train model) + (collect new rollouts with that model) = a single "iteration"
    ############################################################################################

    def save_training_info(self, save_data):

        if self.iter_num==-7:
            print("Error: MUST SPECIFY ITER_NUM FOR SAVER...")
            import IPython
            IPython.embed()

        pickle.dump(
            save_data.train_rollouts_onPol,
            open(
                self.save_dir + '/training_data/train_rollouts_onPol_final.pickle',
                'wb'),
            protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(
            save_data.val_rollouts_onPol,
            open(
                self.save_dir + '/training_data/val_rollouts_onPol_final.pickle',
                'wb'),
            protocol=pickle.HIGHEST_PROTOCOL)

        # mean/std info
        pickle.dump(
            save_data.normalization_data,
            open(
                self.save_dir + '/training_data/normalization_data_final.pickle',
                'wb'),
            protocol=pickle.HIGHEST_PROTOCOL)

        #on-policy training data (used in conjunction w random training data) to train the dynamics model at this iteration
        if self.iter_num%50 == 0:
            pickle.dump(
                save_data.train_rollouts_onPol,
                open(
                    self.save_dir + '/training_data/train_rollouts_onPol_iter' +
                    str(self.iter_num) + '.pickle', 'wb'),
                protocol=pickle.HIGHEST_PROTOCOL)
            pickle.dump(
                save_data.val_rollouts_onPol,
                open(
                    self.save_dir + '/training_data/val_rollouts_onPol_iter' + str(
                        self.iter_num) + '.pickle', 'wb'),
                protocol=pickle.HIGHEST_PROTOCOL)

            #mean/std info
            pickle.dump(
                save_data.normalization_data,
                open(
                    self.save_dir + '/training_data/normalization_data_' + str(
                        self.iter_num) + '.pickle', 'wb'),
                protocol=pickle.HIGHEST_PROTOCOL)

        #losses and sample complexity
        np.save(self.save_dir + '/losses/list_training_loss.npy',
                save_data.pddm_training_losses)
        np.save(self.save_dir + '/losses/distrib_list_training_loss.npy',
                save_data.distrib_training_losses)
        np.save(self.save_dir + '/datapoints_per_agg.npy',
                save_data.training_numData)

        np.save(self.save_dir + '/losses/training_losses_final.npy',
                save_data.pddm_training_lists_to_save['training_loss_list'])
        np.save(self.save_dir + '/losses/validation_losses_final.npy',
                save_data.pddm_training_lists_to_save['val_loss_list_rand'])
        np.save(self.save_dir + '/losses/validation_losses_xaxis_final.npy',
                save_data.pddm_training_lists_to_save['val_loss_list_xaxis'])
        np.save(self.save_dir + '/losses/validation_onPol_losses_final.npy',
                save_data.pddm_training_lists_to_save['val_loss_list_onPol'])
        np.save(self.save_dir + '/losses/old_losses_final.npy',
                save_data.pddm_training_lists_to_save['rand_loss_list'])
        np.save(self.save_dir + '/losses/new_losses_final.npy',
                save_data.pddm_training_lists_to_save['onPol_loss_list'])

        np.save(self.save_dir + '/losses/distrib_training_losses_final.npy',
                save_data.distrib_training_lists_to_save['training_loss_list'])
        np.save(self.save_dir + '/losses/distrib_actual_rewards_final.npy',
                save_data.distrib_training_lists_to_save['actual_rewards_list'])
        np.save(self.save_dir + '/losses/distrib_predicted_val_dist_final.npy',
                save_data.distrib_training_lists_to_save['predicted_val_dist_list'])
        np.save(self.save_dir + '/losses/distrib_predicted_reward_final.npy',
                save_data.distrib_training_lists_to_save['predicted_reward_list'])
        np.save(self.save_dir + '/losses/distib_m_prob_final.npy',
                save_data.distrib_training_lists_to_save['m_prob_list'])

        if self.iter_num%50 == 0:
            #train/val losses from model training
            np.save(self.save_dir + '/losses/training_losses_iter' + str(self.iter_num)
                    + '.npy', save_data.pddm_training_lists_to_save['training_loss_list'])
            np.save(self.save_dir + '/losses/validation_losses_iter' + str(self.iter_num)
                    + '.npy', save_data.pddm_training_lists_to_save['val_loss_list_rand'])
            np.save(self.save_dir + '/losses/validation_losses_xaxis_iter' + str(self.iter_num)
                    + '.npy', save_data.pddm_training_lists_to_save['val_loss_list_xaxis'])
            np.save(self.save_dir + '/losses/validation_onPol_losses_iter' + str(self.iter_num)
                    + '.npy', save_data.pddm_training_lists_to_save['val_loss_list_onPol'])
            np.save(self.save_dir + '/losses/old_losses_iter' + str(self.iter_num)
                    + '.npy', save_data.pddm_training_lists_to_save['rand_loss_list'])
            np.save(self.save_dir + '/losses/new_losses_iter' + str(self.iter_num)
                    + '.npy', save_data.pddm_training_lists_to_save['onPol_loss_list'])

            np.save(self.save_dir + '/losses/distrib_training_losses_iter' + str(self.iter_num)
                    + '.npy', save_data.distrib_training_lists_to_save['training_loss_list'])
            np.save(self.save_dir + '/losses/distrib_actual_rewards_iter' + str(self.iter_num)
                    + '.npy', save_data.distrib_training_lists_to_save['actual_rewards_list'])
            np.save(self.save_dir + '/losses/distrib_predicted_val_dist_iter' + str(self.iter_num)
                    + '.npy', save_data.distrib_training_lists_to_save['predicted_val_dist_list'])
            np.save(self.save_dir + '/losses/distrib_predicted_reward_iter' + str(self.iter_num)
                    + '.npy', save_data.distrib_training_lists_to_save['predicted_reward_list'])
            np.save(self.save_dir + '/losses/distib_m_prob_iter' + str(self.iter_num)
                    + '.npy', save_data.distrib_training_lists_to_save['m_prob_list'])

    def save_rollout_info(self, save_data):

        if self.iter_num==-7:
            print("Error: MUST SPECIFY ITER_NUM FOR SAVER...")
            import IPython
            IPython.embed()

        pickle.dump(
            save_data.rollouts_info,
            open(
                self.save_dir + '/saved_rollouts/rollouts_info_final.pickle',
                'wb'),
            protocol=pickle.HIGHEST_PROTOCOL)

        #info from all MPC rollouts (from this iteration)
        if self.iter_num%50 == 0:
            pickle.dump(
                save_data.rollouts_info,
                open(
                    self.save_dir + '/saved_rollouts/rollouts_info_' + str(
                        self.iter_num) + '.pickle', 'wb'),
                protocol=pickle.HIGHEST_PROTOCOL)

        #save rewards and scores (for rollouts from all iterations thus far)
        np.save(self.save_dir + '/rollouts_rewardsPerIter.npy',
                save_data.rollouts_rewardsPerIter)
        np.save(self.save_dir + '/rollouts_scoresPerIter.npy',
                save_data.rollouts_scoresPerIter)

        #plot rewards and scores (for rollouts from all iterations thus far)
        rew = np.array(save_data.rollouts_rewardsPerIter)
        scores = np.array(save_data.rollouts_scoresPerIter)
        plot_mean_std(rew[:, 0], rew[:, 1], self.save_dir + '/rewards_perIter')
        plot_mean_std(scores[:, 0], scores[:, 1],
                      self.save_dir + '/scores_perIter')

        self.iter_num = -7
