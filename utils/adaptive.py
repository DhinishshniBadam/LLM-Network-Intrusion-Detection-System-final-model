import numpy as np

def dynamic_threshold(probabilities):
    mean = np.mean(probabilities)
    std = np.std(probabilities)
    return mean + std

# threshold = dynamic_threshold(probs)

# if max(probs[i]) > threshold:
#     label = pred[i]
# else:
#     label = "suspicious"
def apply_threshold(probs, pred, i):
    threshold = dynamic_threshold(probs)
    if max(probs[i]) > threshold:
        return pred[i]
    return "suspicious"