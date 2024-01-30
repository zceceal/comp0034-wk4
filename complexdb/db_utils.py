from pathlib import Path

import pandas as pd
from sqlalchemy import and_

from complexdb.models import Prediction, Temperature, Bloom


def add_data(db):
    """ Adds data to the database where there are relations

    This add_data function was called within an application context in create_app, so no need to create a context
    again when you access the database

    Args:
        db (SQLAlchemy object): The initialised SQLAlchemy database object that has been initialised for this app
    """

    # Check if there are any rows in each table, returns None if there are no rows
    # exists_pred = db.session.execute(db.select(Prediction)).scalars().one_or_none()
    count_pred = db.session.scalar(db.select(db.func.count()).select_from(Prediction))
    print("num pred", count_pred)
    # exists_temp = db.session.execute(db.select(Temperature)).scalars().one_or_none()
    count_temp = db.session.scalar(db.select(db.func.count()).select_from(Temperature))
    print("num temp", count_temp)
    # exists_bloom = db.session.execute(db.select(Bloom)).scalars().one_or_none()
    count_bloom = db.session.scalar(db.select(db.func.count()).select_from(Bloom))
    print("num bloom", count_temp)

    # If the result is None for any of the tables, start to add data
    if not count_pred or not count_bloom or not count_temp:
        # Create a connection to the database
        # You passed db to this add_data function as a parameter (see docstring)
        # You can create a connection with the code below, see https://docs.sqlalchemy.org/en/20/core/connections.html
        # You need the connection for the pandas to_sql method
        engine = db.get_engine()
        connection = engine.connect()

        # Use pandas to load the data
        # The dataset is in the same directory as this code file
        dataset = Path(__file__).parent.joinpath("dataset.csv")

        # BLOOM TABLE

        # Find a table that has no foreign keys, e.g. Bloom and populate that first
        if not count_bloom:
            # Get the column with values for Bloom.day_of_year (this is the 'doy' column from the dataframe).
            df_bloom = pd.read_csv(dataset, usecols=['doy'])
            # Rename to match the database column name
            df_bloom = df_bloom.rename(columns={'doy': "day_of_year"})
            # Get unique values by dropping duplicates
            df_bloom = df_bloom.drop_duplicates()
            # Sort the values (not really necessary)
            df_bloom = df_bloom.sort_values(by=['day_of_year'])
            # Add these unique values to the 'bloom' table
            # name='bloom' is the table name in the database
            # con=connection is the connection variable you created above
            # if_exists='append' means don't try to create a new bloom table, append the data to the existing table
            # index=False do not add the Pandas row number, let SQLAlchemy add the auto increment bloom_id instead
            df_bloom.to_sql(name='bloom', con=connection, if_exists='append', index=False)
            connection.commit()

        # TEMPERATURE TABLE

        # This also has no foriegn keys so we can insert data to the database table using the same method as for Bloom

        if not count_temp:
            cols = ["temp", "temp_upper", "temp_lower"]
            df_temp = pd.read_csv(dataset, usecols=cols)
            # Rename to match the database column name
            df_temp = df_temp.rename(columns={"temp": "temp_mean"})
            # Get unique values, this will take rows where the combination of the 3 columns is unique.
            # I've assumed this is what was intended.
            # You can drop based on one column only using subset=['colname']
            df_temp = df_temp.drop_duplicates()
            # Add these unique values to the 'temperature' table
            # name='temperature' is the table name in the database
            # con=connection is the connection variable you created above
            # if_exists='append' means don't try to create a new bloom table, append the data to the existing table
            # index=False do not add the Pandas row number, let SQLAlchemy add the auto increment bloom_id instead
            df_temp.to_sql(name='temperature', con=connection, if_exists='append', index=False)
            connection.commit()

        # PREDICTION TABLE

        # This needs the other two tables to be populated first.
        # You need to find the bloom_id and the temp_id that match the values for each prediction row
        # and then insert the prediction with those foreign keys
        if not count_pred:
            # Load the dataset with all the cols and rename for clarity
            cols = ["year", "doy", "temp", "temp_upper", "temp_lower"]
            df_pred = pd.read_csv(dataset, usecols=cols)
            df_pred = df_pred.rename(columns={"temp": "temp_mean", "doy": "day_of_year"})
            # iterate the years
            for index, row in df_pred.iterrows():
                # Find the bloom_id by searching the bloom table for the 'day_of_year' value for this row in the
                # prediction dataframe
                bloom = db.session.execute(
                    db.select(Bloom).where(Bloom.day_of_year == row['day_of_year'])).scalar()
                print("bloom_id", bloom.bloom_id)
                # Find the temp_id by searching the temp table for the 'temp_mean' AND 'temp_upper' AND 'temp_lower'
                # values that match this row in the prediction dataframe
                # You have to add to the imports 'from sqlalchemy import and_' to be able to use AND
                # The syntax
                temp = db.session.execute(db.select(Temperature).where(and_(
                    Temperature.temp_mean == row['temp_mean'],
                    Temperature.temp_upper == row['temp_upper'],
                    Temperature.temp_lower == row['temp_lower']
                )
                )
                ).scalar()

                # You can then use the id field values to create the new Prediction
                pred = Prediction(year=row['year'], temp_id=temp.temp_id, bloom_id=bloom.bloom_id)

                # Save to the database
                db.session.add(pred)
                db.session.commit()

        # close the connection
        connection.close()
