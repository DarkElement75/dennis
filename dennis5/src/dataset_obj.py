"""
For easily getting an object with the methods and objects we need to access easily in training.

-Blake Edwards / Dark Element
"""

import sys
import numpy as np

import sample_loader
from sample_loader import *

import data_normalization
from data_normalization import *


def get_one_hot_m(v, width):
    #Given vector and width of each one hot, 
    #   get one hot matrix such that each index specified becomes a row in the matrix
    m = np.zeros(shape=(len(v), width))
    m[np.arange(len(v)), v] = 1
    return m

def unison_shuffle(a, b):
    #Shuffle our two arrays while retaining the relation between them
    rng_state = np.random.get_state()
    np.random.shuffle(a)
    np.random.set_state(rng_state)
    np.random.shuffle(b)

def get_data_subsets_lira(archive_dir, subsection_n, p_training=0.8, p_validation=0.1, p_test=0.1):
    """
    Get our dataset array and seperate it into training, validation, and test data
        according to the percentages passed in.

    Defaults:
        80% - Training
        10% - Validation
        10% - Test

    This one is specific for the LIRA implementation, that has inputs as shape (n_samples*64, 80*145).
        In order to shuffle fairly, we divide according to the number of samples, then shuffle.

    This way, we avoid getting a subsection in the training data that is right next to one in the test data, 
        thus getting biased accuracies.
    """
    print "Getting Training, Validation, and Test Data..."

    f = gzip.open(archive_dir, 'rb')
    data = cPickle.load(f)

    n_samples = int(data[0].shape[0]//subsection_n)
    data[0] = np.split(data[0], n_samples)
    data[1] = np.split(data[1], n_samples)

    training_data = [[], []]
    validation_data = [[], []]
    test_data = [[], []]

    n_training_subset = np.floor(p_training*n_samples)
    n_validation_subset = np.floor(p_validation*n_samples)
    #Assign this to it's respective percentage and whatever is left
    n_test_subset = n_samples - n_training_subset - n_validation_subset

    #Shuffle while retaining element correspondence
    print "Shuffling data..."
    unison_shuffle(data[0], data[1])

    #Get actual subsets
    data_x_subsets = np.split(data[0], [n_training_subset, n_training_subset+n_validation_subset])#basically the lines we cut to get our 3 subsections
    data_y_subsets = np.split(data[1], [n_training_subset, n_training_subset+n_validation_subset])

    training_data[0] = data_x_subsets[0]
    validation_data[0] = data_x_subsets[1]
    test_data[0] = data_x_subsets[2]

    training_data[1] = data_y_subsets[0]
    validation_data[1] = data_y_subsets[1]
    test_data[1] = data_y_subsets[2]

    """
    Now that we've shuffled and split relative to images(instead of subsections), collapse back to matrix (or vector if Y)
        We do -1 so that it infers we want to combine the first two dimensions, and we have the last argument because we
        want it to keep the same last dimension. repeat this for all of the subsets
    Since Y's are just vectors, we can easily just flatten
    """
    training_data[0] = training_data[0].reshape(-1, training_data[0].shape[-1])
    training_data[1] = training_data[1].flatten()
    validation_data[0] = validation_data[0].reshape(-1, validation_data[0].shape[-1])
    validation_data[1] = validation_data[1].flatten()
    test_data[0] = test_data[0].reshape(-1, test_data[0].shape[-1])
    test_data[1] = test_data[1].flatten()

    print "# of Samples per subset:"
    print "\t{}".format(training_data[0].shape[0]/64)
    print "\t{}".format(validation_data[0].shape[0]/64)
    print "\t{}".format(test_data[0].shape[0]/64)

    print "Check to make sure these have all the different classes"
    print validation_data[1]
    print list(test_data[1])

    return training_data, validation_data, test_data

def get_data_subsets(archive_dir="../data/mfcc_samples.pkl.gz", p_training=0.8, p_validation=0.1, p_test=0.1):
    """
    Get our dataset array and seperate it into training, validation, and test data
        according to the percentages passed in.

    Defaults:
        80% - Training
        10% - Validation
        10% - Test

    This one is our general function, which will work unless we have a strange dataset bias situation as in the LIRA example.
    """

    print "Getting Training, Validation, and Test Data..."
    f = gzip.open(archive_dir, 'rb')
    data = cPickle.load(f)

    n_samples = len(data[0])

    #Now we split our samples according to percentage
    training_data = [[], []]
    validation_data = [[], []]
    test_data = [[], []]


    n_training_subset = np.floor(p_training*n_samples)
    n_validation_subset = np.floor(p_validation*n_samples)
    #Assign this to it's respective percentage and whatever is left
    n_test_subset = n_samples - n_training_subset - n_validation_subset

    #Shuffle while retaining element correspondence
    print "Shuffling data..."
    unison_shuffle(data[0], data[1])

    #Get actual subsets
    data_x_subsets = np.split(data[0], [n_training_subset, n_training_subset+n_validation_subset])#basically the lines we cut to get our 3 subsections
    data_y_subsets = np.split(data[1], [n_training_subset, n_training_subset+n_validation_subset])

    training_data[0] = data_x_subsets[0]
    validation_data[0] = data_x_subsets[1]
    test_data[0] = data_x_subsets[2]

    training_data[1] = data_y_subsets[0]
    validation_data[1] = data_y_subsets[1]
    test_data[1] = data_y_subsets[2]

    return training_data, validation_data, test_data

"""
NECESSARY FORMATS
Each subset must be the following format:
    [x, y]
        x shape: (number of samples, length of input vector)
            where the values are samples, and inputs for each
        y shape: (number of samples, one hot output vector)
            where the values are samples, and a one hot vector of outputs for each

So in the case of MNIST, we'd have 
x: (20, 784)
y: (20, 10) 

if there were only 20 images.
"""

#Called by outside of this, uses the classes defined in this file to return dataset object
def load_dataset_obj(p_training, p_validation, p_test, archive_dir, output_dims, data_normalization=True, lira_data=False, subsection_n=0):
    #Obtain datasets
    if lira_data:
        #Use our subsection_n and sample_loader specific function
        training_data, validation_data, test_data = get_data_subsets_lira(archive_dir, subsection_n, p_training = p_training, p_validation = p_validation, p_test = p_test)
    else:
        training_data, validation_data, test_data = get_data_subsets(archive_dir, p_training = p_training, p_validation = p_validation, p_test = p_test)
        
    #Do whole data normalization on our input data, by getting the mean and stddev of the training data,
    #Then keeping these metrics and applying to the other data subsets
    if data_normalization:
        input_normalizer_mean, input_normalizer_stddev = generate_input_normalizer(training_data)
    else:
        input_normalizer_mean = 0.0
        input_normalizer_stddev = 1.0
    normalization_data = [input_normalizer_mean, input_normalizer_stddev]

    training_data = normalize_input(training_data, input_normalizer_mean, input_normalizer_stddev)
    validation_data = normalize_input(validation_data, input_normalizer_mean, input_normalizer_stddev)
    test_data = normalize_input(test_data, input_normalizer_mean, input_normalizer_stddev)

    #Convert ys in each to one hot vectors
    training_data[1] = get_one_hot_m(training_data[1], output_dims)
    validation_data[1] = get_one_hot_m(validation_data[1], output_dims)
    test_data[1] = get_one_hot_m(test_data[1], output_dims)

    #return dataset obj
    return Dataset(training_data, validation_data, test_data), normalization_data
    

class Dataset(object):

    #Initialize our data subset objects
    def __init__(self, training_data, validation_data, test_data):
        self.training = training_subset(training_data)
        self.validation = validation_subset(validation_data)
        self.test = test_subset(test_data)

    #Get a new mb_n number of entries from our training subset, after shuffling both sides in unison
    def next_batch(self, mb_n):
        #Shuffle our training dataset,
        #Return first mb_n elements of shuffled dataset
        unison_shuffle(self.training.x, self.training.y)
        return [self.training.x[:mb_n], self.training.y[:mb_n]]

#So we assure we have the same attributes for each subset
class DataSubset(object):
    def __init__(self, data):
        #self.whole_data = data
        self.x = data[0]
        self.y = data[1]

class training_subset(DataSubset):
    def __init__(self, data):
        DataSubset.__init__(self, data)

class validation_subset(DataSubset):
    def __init__(self, data):
        DataSubset.__init__(self, data)

class test_subset(DataSubset):
    def __init__(self, data):
        DataSubset.__init__(self, data)
