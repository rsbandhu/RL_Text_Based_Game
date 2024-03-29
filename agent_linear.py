"""Linear QL agent"""
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import framework
import utils

DEBUG = False


GAMMA = 0.5  # discounted factor
TRAINING_EP = 0.5  # epsilon-greedy parameter for training
TESTING_EP = 0.05  # epsilon-greedy parameter for testing
NUM_RUNS = 10
NUM_EPOCHS = 600
NUM_EPIS_TRAIN = 25  # number of episodes for training at each epoch
NUM_EPIS_TEST = 50  # number of episodes for testing
ALPHA = 0.001  # learning rate for training

ACTIONS = framework.get_actions()
OBJECTS = framework.get_objects()
NUM_ACTIONS = len(ACTIONS)
NUM_OBJECTS = len(OBJECTS)


def tuple2index(action_index, object_index):
    """Converts a tuple (a,b) to an index c"""
    return action_index * NUM_OBJECTS + object_index


def index2tuple(index):
    """Converts an index c to a tuple (a,b)"""
    return index // NUM_OBJECTS, index % NUM_OBJECTS


# pragma: coderesponse template name="linear_epsilon_greedy"
def epsilon_greedy(state_vector, theta, epsilon):
    """Returns an action selected by an epsilon-greedy exploration policy

    Args:
        state_vector (np.ndarray): extracted vector representation
        theta (np.ndarray): current weight matrix
        epsilon (float): the probability of choosing a random command

    Returns:
        (int, int): the indices describing the action/object to take
    """

    if np.random.rand() < epsilon: # choose a random number with prob = epsilon
        # choose a random action
        (action_index, object_index) = index2tuple(np.random.randint(low = 0, high= NUM_ACTIONS*NUM_OBJECTS))
    else:
        #choose greedy action with prob = 1-epsilon
        (action_index, object_index) = index2tuple(np.argmax(theta @ state_vector))

    #action_index, object_index = None, None

    return (action_index, object_index)
# pragma: coderesponse end


# pragma: coderesponse template
def linear_q_learning(theta, current_state_vector, action_index, object_index,
                      reward, next_state_vector, terminal):
    """Update theta for a given transition

    Args:
        theta (np.ndarray): current weight matrix
        current_state_vector (np.ndarray): vector representation of current state
        action_index (int): index of the current action
        object_index (int): index of the current object
        reward (float): the immediate reward the agent recieves from playing current command
        next_state_vector (np.ndarray): vector representation of next state
        terminal (bool): True if this epsiode is over

    Returns:
        None
    """

    #print("theta shape ", theta.shape)
    #print(" current state vector shape ", current_state_vector.shape)
    #print("NUM objects ", NUM_OBJECTS, "  num actions  ", NUM_ACTIONS)

    theta_idx = tuple2index(action_index, object_index)
    cur_q_value = (theta @ current_state_vector)[theta_idx]
    max_q_value = 0 if terminal else np.max(theta @ next_state_vector)
    target = reward + GAMMA* max_q_value

    del_theta = (target - cur_q_value)*current_state_vector.T

    #print(del_theta.shape, theta[theta_idx,:].shape)
    #print(action_index, object_index, theta_idx)

    theta[theta_idx, :] = theta[theta_idx, :] + ALPHA * del_theta
    #theta = theta + ALPHA * (target - theta @ current_state_vector)*current_state_vector # TODO Your update here
# pragma: coderesponse end


def run_episode(for_training):
    """ Runs one episode
    If for training, update Q function
    If for testing, computes and return cumulative discounted reward

    Args:
        for_training (bool): True if for training

    Returns:
        None
    """
    epsilon = TRAINING_EP if for_training else TESTING_EP
    epi_reward = None

    # initialize for each episode

    epi_reward = 0
    gamma_t = 1

    (current_room_desc, current_quest_desc, terminal) = framework.newGame()
    while not terminal:
        # Choose next action and execute
        current_state = current_room_desc + current_quest_desc
        current_state_vector = utils.extract_bow_feature_vector(
            current_state, dictionary)
        # TODO Your code here
        # choose the next action based on epsilon greedy policy
        (action_index, object_index) = epsilon_greedy(current_state_vector, theta, epsilon)

        #go to the next state based on the action
        (next_room_desc, next_quest_desc, reward, terminal) = framework.step_game(current_room_desc, current_quest_desc,
                                                                                  action_index, object_index)

        # extract the feature vector of the next state
        next_state = next_room_desc + next_quest_desc
        next_state_vector = utils.extract_bow_feature_vector(next_state, dictionary)

        if for_training:
            # update Q-function.
            # TODO Your code here

            #update the theta based on the states, action and reward
            linear_q_learning(theta, current_state_vector, action_index, object_index,
                              reward, next_state_vector, terminal)
            #pass

        if not for_training:
            # update reward
            # TODO Your code here
            #update total reward for test case
            epi_reward += gamma_t * reward
            #pass

        # prepare next step
        # TODO Your code here
        current_room_desc = next_room_desc
        current_quest_desc = next_quest_desc
        gamma_t = gamma_t * GAMMA

    if not for_training:
        return epi_reward


def run_epoch():
    """Runs one epoch and returns reward averaged over test episodes"""
    rewards = []

    for _ in range(NUM_EPIS_TRAIN):
        run_episode(for_training=True)

    for _ in range(NUM_EPIS_TEST):
        rewards.append(run_episode(for_training=False))

    return np.mean(np.array(rewards))


def run():
    """Returns array of test reward per epoch for one run"""
    global theta
    theta = np.zeros([action_dim, state_dim])

    single_run_epoch_rewards_test = []
    pbar = tqdm(range(NUM_EPOCHS), ncols=80)
    for _ in pbar:
        single_run_epoch_rewards_test.append(run_epoch())
        pbar.set_description(
            "Avg reward: {:0.6f} | Ewma reward: {:0.6f}".format(
                np.mean(single_run_epoch_rewards_test),
                utils.ewma(single_run_epoch_rewards_test)))
    return single_run_epoch_rewards_test


if __name__ == '__main__':
    state_texts = utils.load_data('game.tsv')
    dictionary = utils.bag_of_words(state_texts)
    state_dim = len(dictionary)
    action_dim = NUM_ACTIONS * NUM_OBJECTS

    # set up the game
    framework.load_game_data()

    epoch_rewards_test = []  # shape NUM_RUNS * NUM_EPOCHS

    for _ in range(NUM_RUNS):
        epoch_rewards_test.append(run())

    epoch_rewards_test = np.array(epoch_rewards_test)

    x = np.arange(NUM_EPOCHS)
    fig, axis = plt.subplots()
    axis.plot(x, np.mean(epoch_rewards_test,
                         axis=0))  # plot reward per epoch averaged per run
    axis.set_xlabel('Epochs')
    axis.set_ylabel('reward')
    axis.set_title(('Linear: nRuns=%d, Epilon=%.2f, Epi=%d, alpha=%.4f' %
                    (NUM_RUNS, TRAINING_EP, NUM_EPIS_TRAIN, ALPHA)))

