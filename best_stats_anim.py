"""
    replication of animation presented by Hans Rosling on his TED talk 
    'The best stats you've ever seen'

    @author: Guillaume Martin
    @data: 2018-07-12
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def preprocess_df(df, value_name):

    """ remove missing values and put years in one column
    
    Parameters
    ----------
    df: dataframe
        the data that needs to be preprocessed

    value_name: string
        the name of the column that will contain the year's data

    Return
    ------
    preprocessed dataframe
    """
    years = [str(y) for y in range(1960, 2017)]
    
    # remove useless columns
    df.drop(['Country Name', 'Indicator Name', 'Indicator Code',
           '2017', 'Unnamed: 62'], axis=1, inplace=True)

    # remove countries with missing value
    df.dropna(axis=0, inplace=True)

    # melt the dataframe to have years in one columns
    df = pd.melt(df,
                 id_vars='Country Code',
                 value_vars=years,
                 var_name='Year',
                 value_name=value_name)

    return df


    # Load the data
    country = pd.read_csv('country_metadata.csv')
    population = pd.read_csv('country_population.csv', skiprows=4)
    fertility_rate = pd.read_csv('fertility_rate.csv', skiprows=4)
    life_expectancy = pd.read_csv('life_expectancy.csv', skiprows=4)

    country = country[['Country Code', 'Region']]

    population = preprocess_df(population, 'Population')
    fertility_rate = preprocess_df(fertility_rate, 'Fertility Rate')
    life_expectancy = preprocess_df(life_expectancy, 'Life Expectancy')

    # Merge the data into one dataframe
    df = pd.merge(country, population, how='left', on='Country Code')
    df = pd.merge(df, life_expectancy, how='left', on=['Country Code', 'Year'])
    df = pd.merge(df, fertility_rate, how='left', on=['Country Code', 'Year'])

    # Remove remaining lines with missing values
    # They will appear if a country is in one dataframe but not in another one
    df.dropna(axis=0, inplace=True)
    print(df.head())
    return df

def main(output):
    # Load the data
    country = pd.read_csv('country_metadata.csv')
    population = pd.read_csv('country_population.csv', skiprows=4)
    fertility_rate = pd.read_csv('fertility_rate.csv', skiprows=4)
    life_expectancy = pd.read_csv('life_expectancy.csv', skiprows=4)

    country = country[['Country Code', 'Region']]

    population = preprocess_df(population, 'Population')
    fertility_rate = preprocess_df(fertility_rate, 'Fertility Rate')
    life_expectancy = preprocess_df(life_expectancy, 'Life Expectancy')

    # Merge the data into one dataframe
    df = pd.merge(country, population, how='left', on='Country Code')
    df = pd.merge(df, life_expectancy, how='left', on=['Country Code', 'Year'])
    df = pd.merge(df, fertility_rate, how='left', on=['Country Code', 'Year'])

    # Remove remaining lines with missing values
    # They will appear if a country is in one dataframe but not in another one
    df.dropna(axis=0, inplace=True)

    # Generate the animation
    years = df['Year'].unique().tolist()

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(df['Fertility Rate'].min() - .3,
                df['Fertility Rate'].max() + .3)
    ax.set_ylim(df['Life Expectancy'].min() - 2,
                df['Life Expectancy'].max() + 2)

    # define visualization
    colors = {
        'Latin America & Caribbean': '#2CA02C',
        'South Asia': '#8C564B',
        'Sub-Saharan Africa': '#E377C2',
        'Europe & Central Asia': '#FF7F0E',
        'Middle East & North Africa': '#D62728',
        'East Asia & Pacific': '#1F77B4',
        'North America': '#9467BD'
    }

    scats = []
    groups = df.groupby('Region')
    for name, grp in groups:
        scat = ax.scatter([], [],
                        marker='o',
                        color=colors[name],
                        label=name,
                        edgecolor='silver',
                        alpha=.6)
        scats.append(scat)

    year_label = ax.text(4.5, 50, '', va='center', ha='center', alpha=.1,
                        size=32, fontdict={'weight': 'bold'})
    ax.spines['bottom'].set_color('silver')
    ax.spines['top'].set_color('silver')
    ax.spines['right'].set_color('silver')
    ax.spines['left'].set_color('silver')
    ax.tick_params(
        labelcolor='silver',
        color='silver'
    )
    ax.set_xlabel('Fertility Rate', color='silver')
    ax.set_ylabel('Life Expectancy', color='silver')

    ax.legend(loc=1, fontsize=7)

    # set the initial state
    def init():
        for scat in scats:
            scat.set_offsets([])
        return scats,

    # function that will update the figure with new data
    def update(year):
        for scat, (name, data) in zip(scats, groups):
            sample = data[data['Year'] == year]
            scat.set_offsets(sample[['Fertility Rate', 'Life Expectancy']])
            scat.set_sizes(np.sqrt(sample['Population'] / 10000) * 5)
            year_label.set_text(year)
        return scats,

    ani = animation.FuncAnimation(fig, update, init_func=init,
                                frames=years,
                                interval=200,
                                repeat=True)

    if output == 'save':
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        ani.save(f'best_stat_anim-{timestamp}.gif',
                 dpi=160, writer='imagemagick')
    else:
        plt.show()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        output = sys.argv[1]
    else:
        print('No output has been defined. Please choose on:\n\
               - show: the animation is displayed on the screen\n\
               - save: the animation is saved as a gif file)')
        sys.exit()

    main(output)
