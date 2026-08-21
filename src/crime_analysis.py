import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# SF Open Data: Police Department Incident Reports
URL = "https://data.sfgov.org/api/views/wg3w-h783/rows.csv?accessType=DOWNLOAD"


class Functions:
    """EDA and plotting helpers for the SF crime incident dataset."""

    @staticmethod
    def explore_data(data):
        print("You can view the exploratory data analysis here:")
        print(data.describe())
        print("Information of the DataFrame is found here:")
        print(data.info())

    @staticmethod
    def convert_to_24_hour(time_string):
        try:
            parts = time_string.split(':')
            if len(parts) == 2:
                hour = int(parts[0])
                minute = int(parts[1])
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return hour
        except ValueError:
            pass
        return "Invalid time format"

    @staticmethod
    def plot_crime_by_district(dataframe):
        try:
            sns.scatterplot(
                x='Latitude',
                y='Longitude',
                hue='Police District',
                alpha=0.01,
                data=dataframe,
            )
            plt.title('Crime Separated by Police District')
            plt.show()
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    data = pd.read_csv(URL)
    print(data.head())

    Functions.explore_data(data)
    Functions.plot_crime_by_district(data)
