from pydub import AudioSegment
from shutil import copyfile
import os
import logging



#zmieniam format czasu 00:00:50 na milisekundy 50000
def start_in_miliseconds(rbt_preview_start_time):

	hours, minutes, seconds = (["0", "0"] + rbt_preview_start_time.split(":"))[-3:]
	hours = int(hours)
	minutes = int(minutes)
	seconds = float(seconds)
	miliseconds = int(3600000 * hours + 60000 * minutes + 1000 * seconds)
	return miliseconds

#main
def rbt_cut(path_end, input_dic, bip_path, bool_val):
        cd_number = ''
        try:

#PACZKA INSERT = 0 / UPDATE = 1
                delivery_state = 0
                if bool_val == True:
                        delivery_state = 0
                else:
                        delivery_state = 1

        ##listuje katalog albumu
                t_in_album = os.listdir(input_dic['r_path'])

        ##jesli w katologu jest podzial na plyty, listuje wtedy zawartosc samej plyty
                if 'CD'+str(input_dic['t_disc_number']) in t_in_album:
                        t_in_album = os.listdir(input_dic['r_path']+'/CD'+str(input_dic['t_disc_number'])+'/')
                        cd_number = '/CD'+str(input_dic['t_disc_number'])

        #znjaduje szukany track i tworze jego sciezke
                t_title = ''
                t_extension = ''
                for file_name in t_in_album:
                        temp = str(input_dic['t_track_number'])
                        if len(temp) == 1:
                        temp = '0' + temp
                        if temp + ' ' in file_name[0:4]:
                                t_title = file_name
                        if file_name.endswith('.wav'):
                                t_extension = '.wav'
                        elif file_name.endswith('.flac'):
                                t_extension = '.flac'
                        elif file_name.endswith('.mp3'):
                                t_extension = '.mp3'


                t_path = input_dic['r_path'] + cd_number + '/' + t_title

        #przypisuje tracki pod obiekty
                original_track = AudioSegment.from_file(t_path, format=t_extension)
                bip_track_60_sec = AudioSegment.from_file(bip_path, format="mp3")

        #wycinam szukany rbt, dorzucam fade i jego glosnosc
                rbt_start_time = start_in_miliseconds(input_dic['rbt_preview_start_time'])
                track_60_sec = original_track[rbt_start_time: rbt_start_time + 60000]
                track_30_sec = original_track[0:30000]
                track_60_sec = track_60_sec - 7												#moze jeszcze troche sciszyc
                track_60_sec = track_60_sec.fade_in(2500).fade_out(2500)

        #podglasniam BIPa i nakladam go na utwor
                bip_track_60_sec = bip_track_60_sec + 5
                track_60_sec = track_60_sec.overlay(bip_track_60_sec)
                track_60_sec = bip_track_60_sec.overlay(track_60_sec)

        #temp audio - tylko pociete + BIP
                track_60_sec.export(path_end[delivery_state][0]+'/'+'temp.wav', format='wav')
                track_60_sec.export(path_end[delivery_state][0]+'/'+'temp.mp3', format='mp3')

        #gotowe audio pod Orange
                os.system('ffmpeg -i '+'"'+path_end[delivery_state][0]+'/temp.wav'+'"'+' -c:a pcm_alaw -ar 8000 -ac 1 -bitexact '+'"'+path_end[delivery_state][0]+'/'+str(input_dic['orange_id'])+'.wav'+'"')
                os.system('ffmpeg -i '+'"'+path_end[delivery_state][0]+'/temp.mp3'+'"'+' -ar 44100 -ac 1 -ab 64k -id3v2_version 0 '+'"'+path_end[delivery_state][0]+'/'+str(input_dic['orange_id'])+'.mp3'+'"')

        #gotowe audio pod Plus 								-*usniecie tago
                os.system('ffmpeg -i '+'"'+path_end[delivery_state][0]+'/temp.wav'+'"'+' -c:a pcm_alaw -ar 8000 -ac 1 '+'"'+path_end[delivery_state][2]+'/'+str(input_dic['plus_id'])+'.wav'+'"')
                os.system('ffmpeg -i '+'"'+path_end[delivery_state][0]+'/temp.mp3'+'"'+' -ar 44100 -ac 1 -ab 128k '+'"'+path_end[delivery_state][2]+'/'+str(input_dic['plus_id'])+'.mp3'+'"')

                #copyfile(path_end[delivery_state][0]+'/'+str(input_dic['orange_id'])+'.wav', path_end[delivery_state][2]+'/'+str(input_dic['plus_id'])+'.wav')
                #copyfile(path_end[delivery_state][0]+'/'+str(input_dic['orange_id'])+'.mp3', path_end[delivery_state][2]+'/'+str(input_dic['plus_id'])+'.mp3')

        #gotowe audio pod Tmobile
                #os.system('ffmpeg -i '+'"'+path_end[delivery_state][0]+'/temp.wav'+'"'+' -c:a pcm_alaw -ar 8000 -ac 1 '+'"'+path_end[delivery_state][3]+'/'+'ind0'+str(input_dic['tmobile_id'])+'.wav'+'"')
                #os.system('ffmpeg -i '+'"'+path_end[delivery_state][0]+'/temp.mp3'+'"'+' -ar 44100 -ac 1 -ab 64k '+'"'+path_end[delivery_state][3]+'/'+'ind0'+str(input_dic['tmobile_id'])+'.mp3'+'"')

                copyfile(path_end[delivery_state][0]+'/'+str(input_dic['orange_id'])+'.wav', path_end[delivery_state][3]+'/'+'ind0'+str(input_dic['tmobile_id'])+'.wav')
                copyfile(path_end[delivery_state][0]+'/'+str(input_dic['orange_id'])+'.mp3', path_end[delivery_state][3]+'/'+'ind0'+str(input_dic['tmobile_id'])+'.mp3')

        #przygotowanie pod Play
                os.system('ffmpeg -i '+'"'+path_end[delivery_state][0]+'/temp.mp3'+'"'+' -ar 44100 -ac 1 -ab 128k '+'"'+path_end[delivery_state][1]+'/'+'product.mp3'+'"')

                #track_30_sec = original_track[rbt_start_time: rbt_preview_start_time + 30000]
                track_30_sec = track_30_sec.fade_in(2500).fade_out(2500)
                track_30_sec.export(path_end[delivery_state][1]+'/'+'temp.mp3', format='mp3')

        #gotowe audio pod Play
                os.system('ffmpeg -i '+'"'+path_end[delivery_state][1]+'/temp.mp3'+'"'+' -ar 44100 -ac 2 -ab 96k '+'"'+path_end[delivery_state][1]+'/'+'prev_96kbps.mp3'+'"')
                os.system('ffmpeg -i '+'"'+path_end[delivery_state][1]+'/temp.mp3'+'"'+' -ar 44100 -ac 2 -ab 128k '+'"'+path_end[delivery_state][1]+'/'+'prev_128kbps.mp3'+'"')

        #usuwam temp
                os.remove(path_end[delivery_state][0]+'/temp.wav')
                os.remove(path_end[delivery_state][0]+'/temp.mp3')
                os.remove(path_end[delivery_state][1]+'/temp.mp3')

        except BaseException as err:
                logging.warning(err)
                return 1

        return 0
