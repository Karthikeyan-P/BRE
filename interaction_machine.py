from copy import deepcopy
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from scipy.sparse import csr_matrix
from matplotlib import pyplot as plt

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from lightfm import LightFM
from lightfm.evaluation import auc_score, precision_at_k

df = pd.read_csv('data/candy.csv')
df.sample(1)

class InteractionMachine:
    def __init__(self):
        self.user_encoder = LabelEncoder()
        self.item_encoder = LabelEncoder()

    def __repr__(self):
        return 'InteractionMachine()'

    def build(self, users, items, ratings):
        u = self.user_encoder.fit_transform(users)
        i = self.item_encoder.fit_transform(items)
        self.n_users = len(np.unique(u))
        self.n_items = len(np.unique(i))
        self.interactions = csr_matrix((ratings, (u, i)), shape=(self.n_users, self.n_items))
        return self

im = InteractionMachine()
im.build(df['user'], df['item'], df['review'])
im.interactions

### train test split
from lightfm.cross_validation import random_train_test_split

train, test = random_train_test_split(im.interactions, test_percentage=0.2)

# model
model = LightFM(loss='warp')

count = 0
best = 0
auc = []
for e in range(100):
    if count > 5: # patience
        break
    model.fit_partial(train, epochs=1)
    auc_train = auc_score(model, train).mean()
    auc_test = auc_score(model, test).mean()
    print(f'Epoch: {e}, Train AUC={auc_train:.3f}, Test AUC={auc_test:.3f}')
    auc.append((auc_train, auc_test))
    if auc_test > best:
        best_model = deepcopy(model)
        best = auc_test
    else:
        count += 1
model = deepcopy(best_model)

auc = np.array(auc)
plt.plot(auc[:, 0], label='train')
plt.plot(auc[:, 1], label='test')
plt.legend()

precision_at_k(model, train, k=10).mean()
auc_score(model, test).mean()

user = 'aaron67'
df[df['user'] == user]

user_id = user_encoder.transform([user])[0]

preds = model.predict(user_id, list(range(li)))
preds = pd.DataFrame(zip(preds, item_encoder.classes_), columns=['pred', 'item'])
preds = preds.sort_values('pred', ascending=False)

tried = df[df['user'] == user]['item'].values
preds[~preds['item'].isin(tried)]['item'].values[:5]