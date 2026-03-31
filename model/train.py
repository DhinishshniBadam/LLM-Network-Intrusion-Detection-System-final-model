import joblib
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from utils.preprocess import load_data

# load data
X,y = load_data("data/Train_data.csv")

# split data
X_train,X_val,y_train,y_val = train_test_split(X,y,test_size=0.2,random_state=42)

# train model
model = RandomForestClassifier(n_estimators=300,max_depth=20)
model.fit(X_train,y_train)

# validate
pred = model.predict(X_val)

print(classification_report(y_val,pred))
print(confusion_matrix(y_val,pred))

# save model and encoders
from utils.preprocess import get_encoders
encoders = get_encoders("data/Train_data.csv")
joblib.dump({"model":model,"encoders":encoders},"model/ids.pkl")