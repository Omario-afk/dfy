from pytube import YouTube
from pytube.exceptions import RegexMatchError
from tkinter import Tk, filedialog
from tqdm import tqdm
from time import sleep
from os import remove, startfile
from subprocess import run
from termcolor import colored
from urllib.error import HTTPError


try:

    with open('E://Python//Nier//banner.txt', 'r', encoding='utf-8') as banner:

        for line in banner.readlines():
            print(line, end='')

        print('\n\n')

        sleep(1)

except FileNotFoundError:
    pass


def download_from_youtube(youtube_link, audio_only=False, path=None):

    #Youtube separates audio and video. This function will download them separately then merge them in case user wants to download the video, not just the audio.

    if path is None:
        print('Path not specified...')

    def get_audio():
        global Audio_name

        urls_a = YouTube(youtube_link).streams

        if started_v is True:  #Changing name for audio file since they both have same name in order to avoid problems in case they have the same extension.
            audio = urls_a.order_by('audio_codec').desc().first()
            Audio_name = 'audio--' + str(audio.default_filename.split('.')[0])
            print("\nDownloading audio from url... Shouldn't take long...")
            audio.download(path, filename=Audio_name)
            Audio_name = Audio_name + '.' + str(audio.default_filename.split('.')[-1])

        else:
            audio = urls_a.order_by('audio_codec').desc().first()
            Audio_name = audio.default_filename
            print('Title: ', colored(Audio_name.split('.')[0], 'green'))
            print(colored("\nDownloading audio from url... Shouldn't take long...", 'yellow'))
            audio.download(path)

            run('ffmpeg -loglevel quiet -i "{}" "{}"'.format(path + Audio_name, path + str(Audio_name.split('.')[0]) + '.mp3'), shell=True)
            remove(path + Audio_name)

        print('\n Done {}'.format('\u2713'))

    def get_video():

        global Video_name

        global Concat

        def download_progress_v(_, __, bytes_remaining):
            global started_v
            global current_pr_v
            if not started_v:
                current_pr_v = video_to_dl.filesize
                started_v = True
                pass
            else:
                pass
            prv = current_pr_v - bytes_remaining  # Bytes downloaded with each iteration, current_pr > bytes_remaining.
            progress_bar_video.update(prv/1000000)
            current_pr_v = bytes_remaining  # assigning the bytes_remaining value to msg constant variable.

        urls = YouTube(youtube_link, on_progress_callback=download_progress_v).streams

        video_Dict = {}

        videos = urls.filter(video_codec="vp9").order_by('resolution').desc()

        print('\n      [Res]  |   [FPS]  |  [Size]\n   - - - - - - - - - - - - - - - - - \n        |          |          |\n        V          V          V')

        i = 1

        for video in videos:

            information = str(video).split(' ')
            print_info = '| '

            for info in information:

                if 'res=' in info:
                    info = str(info.split('=')[1])
                    if '144p' in info or '240p' in info or '360p' in info or '480p' in info or '720p' in info:
                        space = '  |  '
                    else:
                        space = ' |  '
                    print_info = print_info + info + space

                if 'fps=' in info:
                    info = str(info.split('=')[-1])
                    print_info = print_info + info

                size = int(video.filesize/1000000)  #10*-6 from Bytes to MegaBytes.

                # Aligning the size signs: Al = alignment.
                if size > 1000:
                    size = int(video.filesize/1000000000)  #10*-9 from Bytes to GigaBytes.
                    Al = '     -GB'

                elif 100 <= size < 1000:
                    Al = '   -MB'

                elif 10 <= size < 100:
                    Al = '    -MB'

                elif 1 <= size < 10:
                    Al = '     -MB'

                elif size < 1:

                    size = int(video.filesize/1000)  #10*-3 from Bytes to KiloBytes.
                    if 100 <= size < 1000:
                        Al = '   -KB'

                    elif 10 <= size < 100:
                        Al = '    -KB'

                size_info = str(size) + Al

            print(str(i) + ') ' + print_info + ' | ' + size_info, end='\n')

            video_Dict[str(i)] = print_info

            i += 1

        while True:

            choice = input('   - - - - - - - - - - - - - - - - - \n Enter msg number to download: ')

            if choice in (key for key in video_Dict):

                choice_res = video_Dict[choice].replace('|', '').replace(' ', '').split('"')[1]  # type is str

                choice_fps = int(str(video_Dict[choice].replace('|', '').replace(' ', '').split('"')[3]).replace('fps', ''))

                video_to_dl = urls.filter(resolution=choice_res, fps=choice_fps).first()

                break

            else:
                pass

        print('\nDownloading video from url... ')

        new_size_for_video = video_to_dl.filesize/1000000
        progress_bar_video = tqdm(total=new_size_for_video, unit='MB', unit_scale=1, position=0, leave=True)

        Video_name = video_to_dl.default_filename

        video_to_dl.download(output_path=path)  #downloading video (without audio).

        print('\n Done \u2713')

        if video_to_dl.includes_audio_track:
            Concat = False
            pass
        else:
            get_audio()  #downloaing the audio for the same video from same url in download_from_youtube.link.

        sleep(1)

    if audio_only is True:
        get_audio()
        return

    else:
        try:
            get_video()
        except HTTPError:
            print("HTTP Error 404: Video not Found\n")

    return


def concat(path):

    Concat_name = Video_name.replace(Video_name.split('.')[-1], 'mkv')

    if '(Official Music Video)' in Concat_name:
        Concat_name = Concat_name.replace('(Official Music Video)', '')

    concat_file = path + Concat_name

    video_file = path + Video_name

    audio_file = path + Audio_name

    #ffmpeg.concat(video_file, audio_file, v=1, msg=1).output(path+Concat_name).run()

    run('ffmpeg -loglevel quiet -i "{}" -i "{}" -c copy "{}"'.format(video_file, audio_file, concat_file))

    if concat_file == video_file:
        pass
    else:
        remove(path+Video_name)

    remove(path + Audio_name)

    return


print('Choose a directory!')

sleep(2)
#Tk().lift()
Tk().withdraw()

Path = filedialog.askdirectory() + '/'

if Path is None:
    Path = 'E://'
    print('No directory has been chosen. Using E:// as directory.', end='')
else:
    print('\nDirectory has been chosen.', end=' ')

while True:

    started_v = False
    current_pr_v = None
    current_pr_a = None
    Audio_name = None
    Video_name = None
    Concat = None

    pass

    while True:
        Link = input('\n-------------------------------\nPaste youtube link ("https://www..."): ')
        if Link.startswith('https://'):
            break
        else:
            pass

    audio_only_choice = input('\n\nDownload audio only? \n   1: Yes\n   .: No\n   c: Cancel\n\n  ->: ').lower()

    if audio_only_choice == '1':
        audio_only_choice = True

    elif audio_only_choice == 'c':
        quit()

    else:
        audio_only_choice = False

    print(colored('\nGetting link info...\n', 'red'))

    try:
        download_from_youtube(youtube_link=Link, audio_only=audio_only_choice, path=Path)
    except RegexMatchError:
        print(colored('\nError! Video not found', 'red'))
        pass

    if audio_only_choice:
        pass
    else:
        try:
            concat(path=Path)
        except AttributeError: pass

    k = input('\nDownload another video? \n  1:  Yes\n  2:  Open Folder\n  -:  Exit\n  -->: ')

    if k == '1':
        pass

    elif k == '2':
        startfile(Path)
        pass

    else:
        quit()
