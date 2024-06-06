from google.transit import gtfs_realtime_pb2
import requests
import datetime as dt
import time # imports module for Epoch/GMT time conversion
from samplebase import SampleBase
from rgbmatrix import graphics
from PIL import Image
import random

home_dir = "~/rpi-rgb-led-matrix"


def get_g_train_times():
    '''
    Gets trains time for greenpoint ave train station and returns strings of formatted times
    north and southbound as a tuple
    '''
    # Get train times for the greenpoint ave train stop
    nb_trains, sb_trains = get_train_times("G", "G26")

    # Format train times
    nb_trains_str = format_train_times(nb_trains)
    sb_trains_str = format_train_times(sb_trains)
    
    return (nb_trains_str, sb_trains_str)


def get_train_times(line, stop):
    '''
    Gets train times in both directions for a given train line and stop
    line: str - train line, only support G now
    stop: stop id according to mta api

    ex: nb_trains, sb_trains = get_train_times("G", "G26")
    '''
    mta_key = "gi6qSN89q3apCTJQh7m967M8mwdZbz5BztXFRDLh"

    if line == "G":
        response = requests.get("https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g",
                        headers={"x-api-key" : mta_key}, allow_redirects=True)
    else:
        raise Exception("Train line not yet supported")



    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    nb_trains = []
    sb_trains = []

    for entity in feed.entity:
        if entity.HasField('trip_update'):

            for update in entity.trip_update.stop_time_update:
                if update.stop_id[:3] == stop:
                    arrival_time = dt.datetime.fromtimestamp(update.arrival.time)
                    if "N" in update.stop_id:
                        nb_trains.append(arrival_time)
                    elif "S" in update.stop_id:
                        sb_trains.append(arrival_time)


    nb_trains.sort()
    sb_trains.sort()

    # Calculate time until train
    now = dt.datetime.now()
    nb_trains = [(t - now).total_seconds() for t in nb_trains]
    sb_trains = [(t - now).total_seconds() for t in sb_trains]

    return (nb_trains, sb_trains)

def format_train_times(train_times, max_times=2):
    '''
    Takes in a list of train times in seconds from current time and formats them for RGB matrix
    '''
    
    tt_str = []

    for t in train_times:
        if t > 60:
            mins = int(t//60)
        elif t > 0:
            mins = ">1"
        else:
            continue

        min_str = f"{mins} min"

        tt_str.append(min_str)
    
    if len(tt_str) > max_times:
        final_str = ", ".join(tt_str[:max_times])
    else:
        final_str = ", ".join(tt_str)

    return(final_str)




class TrainTimes(SampleBase):
    def __init__(self, *args, **kwargs):
        super(TrainTimes, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")
    
    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont(f"{home_dir}/fonts/6x10.bdf")
        small_font = graphics.Font()
        small_font.LoadFont(f"{home_dir}/fonts/4x6.bdf")

        g_logo_thin_fp = f"{home_dir}/display_img/G_logo_cust_thin.ppm"
        g_logo_thin = Image.open(g_logo_thin_fp).convert('RGB')
        g_logo_thin.resize((16, 16), Image.ANTIALIAS)

        # Set color
        dir_textColor = graphics.Color(0, 224, 80)
        time_textColor = graphics.Color(255, 255, 255)

        # Get train times from function
        nb_text, sb_text = get_g_train_times()
        ticker = 0
        rainbow = False
        while True:
            offscreen_canvas.Clear()
            
            # Updaete numbers every 2 seconds
            if ticker % 100 == 0:
                nb_text, sb_text = get_g_train_times()
                if rainbow:
                    red = random.randint(0, 255)
                    green = random.randint(0, 255)
                    blue = random.randint(0, 255)

                    dir_textColor = graphics.Color(red, green, blue)
                    time_textColor = graphics.Color(green, blue, red)
            
            text_pos = 16
            y_offset = -2

            # Train Symbol
            offscreen_canvas.SetImage(g_logo_thin, 0, 0)
            offscreen_canvas.SetImage(g_logo_thin, 0, 16)
            
            # Train direction
            graphics.DrawText(offscreen_canvas, font, text_pos, 10+y_offset, dir_textColor, "Court Sq.")
            graphics.DrawText(offscreen_canvas, font, text_pos, 26+y_offset, dir_textColor, "Church Av.")

            # Train Times
            nb_len = graphics.DrawText(offscreen_canvas, small_font, text_pos, 16+y_offset, time_textColor, nb_text)
            sb_len = graphics.DrawText(offscreen_canvas, small_font, text_pos, 32+y_offset, time_textColor, sb_text)

            # print("pos:", pos, "nb_len:", nb_len, "sb_len:", sb_len)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            ticker += 1
            time.sleep(.1)

    # Old scrolling version
    # def run(self):
    #     offscreen_canvas = self.matrix.CreateFrameCanvas()
    #     font = graphics.Font()
    #     font.LoadFont("../../../fonts/7x13.bdf")
    #     small_font = graphics.Font()
    #     small_font.LoadFont("../../../fonts/6x12.bdf")
    #     # Get train times from functin
    #     nb_text, sb_text = get_g_train_times()
    #     ticker = 0
    #     pos0 = 10
    #     pos = pos0
    #     pos_move = False
    #     pos_forward = True
    #     while True:
    #         offscreen_canvas.Clear()
    #         nb_textColor = graphics.Color(0, 224, 80)
    #         sb_textColor = graphics.Color(255, 255, 255)
    #         if ticker % 250 == 0:
    #             graphics.DrawText(offscreen_canvas, small_font, 4, 14, nb_textColor, "Court Sq.")
    #             graphics.DrawText(offscreen_canvas, small_font, 4, 30, sb_textColor, "Church Av.")
    #             offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
    #             time.sleep(3)
    #         nb_len = graphics.DrawText(offscreen_canvas, font, pos, 14, nb_textColor, nb_text)
    #         sb_len = graphics.DrawText(offscreen_canvas, font, pos, 30, sb_textColor, sb_text)

    #         # print("pos:", pos, "nb_len:", nb_len, "sb_len:", sb_len)
    #         offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

    #         if ticker % 50 == 0 and not pos_move:
    #             pos_move = True
    #         if pos_move and pos_forward:
    #             pos -= 1
    #             if (pos0 - pos) > (nb_len/2 + 7):
    #                 pos_forward = False
    #                 nb_text, sb_text = get_g_train_times()
    #                 time.sleep(3)
    #         elif pos_move:
    #             pos += 1
    #             if pos == pos0:
    #                pos_forward = True
    #                pos_move = False
    #                nb_text, sb_text = get_g_train_times()
    #                time.sleep(3)
    #         if ticker == 0:
    #             time.sleep(3)
    #         else:
    #             time.sleep(0.05)
    #         ticker += 1


if __name__ == "__main__":
    # Debugging
    # nb_gp_trains, sb_gp_trains = get_g_train_times()
    # my_text = ", ".join(nb_gp_trains)
    # print(my_text)
    # Actual code
    train_time = TrainTimes()
    if (not train_time.process()):
        train_time.print_help()





