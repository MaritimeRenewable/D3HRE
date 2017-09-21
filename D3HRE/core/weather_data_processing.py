import numpy as np
from D3HRE.core.navigation_utility import calculate_initial_compass_bearing


def resource_df_processing(dataframe):
    """
    Process downloaded MEERA-2 dataFrame.

    :param dataframe: time indexed Pandas dataFrame contains field of lat, lon, speed,
        local_time, T2M, SWGDN, SWTDN, U2M, V2M
    :return:  time indexed Pandas dataFrame with additional field in temperature (degree C),
        kt(clearness index), V2 (wind speed at 2 metres height), true_wind_direction (degrees),
        heading (degrees), Va (apparent wind speed), apparent_wind_direction(degrees)
    """

    # Temperature processing
    dataframe['temperature'] = dataframe.T2M - 273.15

    # Clearness index processing
    dataframe['kt'] = dataframe.SWGDN / dataframe.SWTDN

    # Wind speed at 2 metres height
    dataframe['V2'] = np.sqrt(dataframe.V2M ** 2 + dataframe.U2M ** 2)

    # Get true wind direction from north ward and east ward wind speed
    dataframe['true_wind_direction'] = (np.degrees(np.arctan2(dataframe['U2M'], dataframe['V2M']))
                                        + 360) % 360

    location_list = [tuple(x) for x in dataframe[['lat', 'lon']].values]

    # Calculate platform heading by compass bearing
    heading = []
    for a, b in zip(location_list[:-1], location_list[1:]):
        heading.append(calculate_initial_compass_bearing(a, b))
    heading.append(heading[-1])
    # Because the platform do not know what the next point to go after reach the
    # last way point we let it stay the same the second last one

    dataframe['heading'] = heading
    # apparent wind                 V_{app} = [Uapp,   Vapp] :: Va
    # true wind at 2 metres height V_{true} = [U2M,     V2M] :: V2
    # platform speed vector           V_{s} = [Up,       Vp] :: Vs
    #
    #                 V_{app} = V_{true} + (- V_{s})

    # Get apparent wind vector and scalar apparent wind speed and direction
    V_s = dataframe['speed'] / 3.6  # ship speed in DataFrame unit of km/h

    U_p = V_s * np.sin(np.radians(dataframe['heading']))
    V_p = V_s * np.cos(np.radians(dataframe['heading']))

    U_app = dataframe['U2M'] - U_p
    V_app = dataframe['V2M'] - V_p

    dataframe['Va'] = np.sqrt(U_app ** 2 + V_app ** 2)
    dataframe['apparent_wind_direction'] = (np.degrees(np.arctan2(U_app, V_app)) +
                                            360) % 360
    return dataframe