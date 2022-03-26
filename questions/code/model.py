import numpy as np
import random

from sklearn.svm import LinearSVC


class Model:
    def __init__(self, train_images, train_labels, num_classes, hp, test_images, test_labels):
        self.input_size = train_images.shape[1]
        self.num_classes = num_classes
        self.num_epochs = hp.num_epochs
        self.learning_rate = hp.learning_rate
        self.batchSz = hp.batch_size
        self.train_images = train_images
        self.train_labels = train_labels
        self.clf = LinearSVC(multi_class='ovr', dual=False)
        self.test_images = test_images
        self.test_labels = test_labels

        # TODO: Set up the weights and biases with the correct shapes
        # Recall that the weights should be of shape
        #           [input_size, number_classes]
        # and that the bias is of shape
        #           [1, number_classes]
        # Fill in the below
        # functions with the correct shapes for both parameters
        self.W = np.random.rand(self.input_size, self.num_classes)
        self.b = np.zeros((1, self.num_classes))

    def forward_pass(self, inputs):
        """
        FORWARD PASS:
        This is where we take our current estimate of the weights and biases
        and compute the current error against the training data.

        Step 1:
        Compute the output response to this 'img' input for each neuron
        (linear unit).
        Our current estimate for the weights and biases are stored in:
            self.W
            self.b
        Remember: use matrix operations.

        Step 2:
        Convert these to probabilities by implementing the softmax function.

        Note that to overcome a runtime overflow warning with softmax, we
        ask that you subtract the value of the greatest logit from all logits
        before exponentiating.

        :param inputs: a batch of train images
        :return: probabilities for each per image
        """
        # TODO: Calculate logits for linear units
        logits = inputs @ self.W + self.b
        logits -= logits.max()
        exp_logits = np.exp(logits)
        # TODO: Get probabilities by using softmax on the logits
        probabilities = np.divide(
            exp_logits, np.sum(exp_logits)
        )
        return probabilities

    @staticmethod
    def loss(probabilities, gt_label):
        """
        Computes the error against the training label 'gt_label' using
        cross-entropy loss
        Remember:
            log has a potential divide by zero error so we recommend adding a
            small number (1E-10) to the probability before taking the log

        :param probabilities: a matrix of shape [batchSz, num_classes]
                containing the probability of each class
        :param gt_label: ground truth label index
        :return: cross-entropy loss
        """
        # TODO: compute loss value
        # Note that while probabilities is [batchSz, num_classes], in our
        # problem, batchSz = 1, so you will have to index into the 0th element
        loss = -np.log(1e-10 + probabilities[0, gt_label])
        return loss

    @staticmethod
    def back_propagation(img, probabilities, gt_label):
        """
        BACKWARD PASS (BACK PROPAGATION):
        This is where we find which direction to move in for gradient descent to
        optimize our weights and biases.
        Use the derivations from the questions handout.

        Compute the delta_W and delta_b gradient terms for the weights and biases
        using the provided derivations in Eqs. 6 and 7 of the handout.
        Remember:
            gradW is a matrix the size of the input by the size of the classes
            gradB is a vector
        Note:
            By equation 6 and 7, we need to subtract 1 from p_j only if it is
            the true class probability.

        :param img: a single image we are updating the weights based on
        :param probabilities: a matrix that contains the probabilities
        :param gt_label: ground truth label index
        :return: gradient for weights, gradient for biases
        """
        # TODO: Back propagation: use gradient descent to update parameters

        # TODO: Reshape train image data to be matrix, dimension [784, 1]
        img_m = img.reshape((-1, 1))
        probabilities_m = probabilities.reshape((1, -1))

        probabilities_m[0, gt_label] -= 1
        gradW, gradB = img_m @ probabilities_m, probabilities_m
        return gradW, gradB

    def gradient_descent(self, gradW, gradB):
        """
        Update self.W and self.b using the gradient terms
        and the self.learning_rate hyperparameter.
        Eqs. 4 and 5 in the handout.

        :param gradW: gradient for weights
        :param gradB: gradient for biases
        :return: None
        """
        # TODO: Modify parameters with summed updates
        self.W -= self.learning_rate * gradW
        self.b -= self.learning_rate * gradB

    def train_nn(self):
        """
        Does the forward pass, loss calculation, and back propagation for this
        model for one step. The neural network is a fully connected layer
        connected with a softmax unit, and the loss funciton is cross-entropy
        loss.

        The basic structure of this part a loop over the number of epoches you
        want to use, for each epoch, you need to iterate every training data.
        The batch size is 1, meaning you should update the parameters for every
        training data.

        Return: None
        """
        indices = list(range(self.train_images.shape[0]))

        for epoch in range(self.num_epochs):
            loss_sum = 0
            random.shuffle(indices)

            for index in range(len(indices)):
                i = indices[index]
                img = self.train_images[i]
                gt_label = self.train_labels[i]

                # TODO: 1. Calculate probabilities from calling forward pass
                #       on img
                probabilities = self.forward_pass(img)

                # TODO: 2. Calculate the loss from probabilities, loss_sum =
                #       loss_sum + your_loss_over_all_classes
                loss_sum += self.loss(probabilities, gt_label)

                # TODO: 3. Calculate gradW, gradB from back propagation
                gradW, gradB = self.back_propagation(img, probabilities, gt_label)

                # TODO: 4. Update self.W and self.B with gradient descent
                self.gradient_descent(gradW, gradB)
                
            # to calculate acuuracy for each epoch on the testing set
            # epoch is a concept for neural network training, so using accuracy_nn for calculation
            accuracy = self.accuracy_nn(self.test_images, self.test_labels)
            print("Epoch " + str(epoch) + ": Total loss: " + str(loss_sum) + "; Accuracy: {:.0%}".format(accuracy))

    def train_svm(self):
        """
        Use the response from the learned weights and biases on the training
        data as input into an SVM. I.E., train an SVM on the multi-class
        hyperplane distance outputs.
        """
        scores = np.dot(self.train_images, self.W) + self.b
        self.clf.fit(scores, self.train_labels)

    def accuracy_nn(self, test_images, test_labels):
        """
        Computes the accuracy of the neural network model over the test set.
        """
        scores = np.dot(test_images, self.W) + self.b
        predicted_classes = np.argmax(scores, axis=1)
        return np.mean(predicted_classes == test_labels)

    def accuracy_svm(self, test_images, test_labels):
        """
        Computes the accuracy of the SVM model over the test set.
        """
        scores = np.dot(test_images, self.W) + self.b
        predicted_classes = self.clf.predict(scores)
        return np.mean(predicted_classes == test_labels)
