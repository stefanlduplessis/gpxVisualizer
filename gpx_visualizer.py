import gpxpy.gpx
import pandas as pd
import matplotlib.pyplot as plt
from geopy import distance
import os


def parse_gpx(gpx_file):
    with open(gpx_file, 'r') as gpx:
        gpx_content = gpx.read()

    gpx = gpxpy.parse(gpx_content)

    data = {
        "lat": [],
        "long": [],
        "dist": [],
        "ele": [],
        "time": [],
        "time_diff": [],
        "speed": [],
        "moving_ave_speed": []
    }

    dist = 0
    time_diff = 0
    speed = 0
    previous_coords = None
    previous_time = None
    first_loop = True

    i_point = 0
    chunk_speed = []
    moving_ave_speed = 0

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                lat = point.latitude if point.latitude else None
                data["lat"].append(lat)
                long = point.longitude if point.longitude else None
                data["long"].append(long)
                ele = point.elevation if point.elevation else None
                data["ele"].append(ele)
                time = point.time if point.time else None
                data["time"].append(time)

                if not first_loop:
                    i_point += 1
                    incremental_distance = distance.distance(previous_coords, (lat, long)).km
                    dist += incremental_distance
                    time_diff = time - previous_time
                    speed = incremental_distance/(time_diff.total_seconds()/3600)

                    chunk_speed.append(speed)
                    if i_point > 10:
                        moving_ave_speed = sum(chunk_speed)/len(chunk_speed)
                        chunk_speed.pop(0)
                else:
                    first_loop = False

                data["dist"].append(dist)
                data["time_diff"].append(time_diff)
                data["speed"].append(speed)
                data["moving_ave_speed"].append(moving_ave_speed)

                previous_coords = (lat, long)
                previous_time = time

    return data, f"{gpx.name} - {str(gpx.time)}"


if __name__ == "__main__":
    directory = "./gpx_dir"
    for filename in os.listdir(directory):
        if filename.endswith(".gpx"):
            data, name = parse_gpx(os.path.join(directory, filename))
            df = pd.DataFrame(data=data)
            df.plot(kind='line', x='long', y='lat', color='red', legend=False).set(xlabel="Longitude", ylabel="Latitude", title="Route")
            df.plot(kind='line', x='dist', y='ele', color='blue', ylim=(0, max(data["ele"]) + 100), title="Elevation", legend=False).set(xlabel="Distance (km)", ylabel="Elevation (m)")
            df.plot(kind='line', x='dist', y='moving_ave_speed', color='orange', title="Speed", legend=False).set(xlabel="Distance (km)", ylabel="Speed (km/h)")
            plt.show()
        else:
            continue

