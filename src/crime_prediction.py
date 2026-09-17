"""
Clustering and classification on SF's live Police Department Incident Reports
feed — a from-scratch rebuild of an original team capstone (K-Means, Decision
Tree, KNN) that had no accuracy figure anywhere in its code. This version
actually computes and prints accuracy for every model, including a naive
baseline, which the original never did.
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

URL = "https://data.sfgov.org/resource/wg3w-h783.csv"
SAMPLE_SIZE = 100000
RANDOM_STATE = 42


def load_data(limit=SAMPLE_SIZE):
    df = pd.read_csv(f"{URL}?$limit={limit}", low_memory=False)
    return df.dropna(subset=[
        "incident_category", "police_district", "latitude", "longitude",
        "incident_year", "incident_day_of_week", "resolution",
    ])


def cluster_by_district(df):
    """K-Means on year/district/category — does clustering recover SF's 11 police districts?"""
    district_le, category_le = LabelEncoder(), LabelEncoder()
    df = df.copy()
    df["district_code"] = district_le.fit_transform(df["police_district"])
    df["category_code"] = category_le.fit_transform(df["incident_category"])

    scaled = StandardScaler().fit_transform(df[["incident_year", "district_code", "category_code"]])
    kmeans = KMeans(init="k-means++", n_clusters=11, n_init=12, random_state=RANDOM_STATE)
    df["cluster"] = kmeans.fit_predict(scaled)
    return df.groupby("cluster")["police_district"].agg(lambda s: s.value_counts().idxmax())


def predict_incident_category(df):
    """Decision tree: how much do district/day/resolution/year tell you about the crime type?"""
    features = pd.get_dummies(
        df[["police_district", "incident_day_of_week", "resolution", "incident_year"]],
        columns=["police_district", "incident_day_of_week", "resolution"],
    )
    X_train, X_test, y_train, y_test = train_test_split(
        features, df["incident_category"], test_size=0.2, random_state=RANDOM_STATE
    )
    clf = DecisionTreeClassifier(criterion="gini", max_depth=10, random_state=RANDOM_STATE)
    clf.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, clf.predict(X_test))
    return accuracy, df["incident_category"].nunique()


def predict_larceny_district(df):
    """KNN: which police district is most at risk for Larceny Theft, with a naive baseline for comparison."""
    larceny = df[df["incident_category"] == "Larceny Theft"].copy()
    features = pd.get_dummies(larceny[["incident_day_of_week", "incident_year"]], columns=["incident_day_of_week"])
    X_train, X_test, y_train, y_test = train_test_split(
        features, larceny["police_district"], test_size=0.2, random_state=RANDOM_STATE
    )
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, y_train)
    knn_accuracy = accuracy_score(y_test, knn.predict(X_test))

    top_district = larceny["police_district"].value_counts().idxmax()
    naive_accuracy = (y_test == top_district).mean()
    return knn_accuracy, naive_accuracy, top_district, larceny["police_district"].nunique()


if __name__ == "__main__":
    print("Loading live SF incident data...")
    data = load_data()
    print(f"Rows after cleaning: {len(data):,}")

    print("\n--- K-Means (11 clusters) ---")
    print(cluster_by_district(data))

    print("\n--- Decision Tree: predict incident_category ---")
    dt_acc, n_classes = predict_incident_category(data)
    print(f"Accuracy: {dt_acc:.4f} across {n_classes} classes")

    print("\n--- KNN: predict district for Larceny Theft ---")
    knn_acc, naive_acc, top, n_districts = predict_larceny_district(data)
    print(f"KNN accuracy: {knn_acc:.4f} | Naive baseline (always '{top}'): {naive_acc:.4f} across {n_districts} districts")
