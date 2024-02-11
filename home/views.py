import subprocess
from django.shortcuts import render
from django.http import HttpResponse
import os
import zipfile
import shutil
import uuid

def downloadForm(request):
    return render(request, 'index.html')

def download(request):
    if request.method == 'POST':
        playlist_url = request.POST.get('playlist_url')
        if not playlist_url:
            return render(request, 'index.html', {'message': 'Please provide a valid playlist URL'})

        try:
            # Generate a unique identifier for this download
            download_id = str(uuid.uuid4())
            # Define the directory where you want to save the downloaded files
            code_folder = os.path.dirname(os.path.abspath(__file__))
            download_directory = os.path.join(code_folder, 'downloaded_music', download_id)

            # Make sure the directory exists, if not, create it
            os.makedirs(download_directory, exist_ok=True)

            # Execute spotdl command to download the playlist
            subprocess.run(['spotdl', '--output', download_directory, playlist_url], check=True)

            # Create a zip file with all downloaded music files
            zip_file_path = os.path.join(code_folder, 'downloaded_music', f'{download_id}.zip')
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                for root, dirs, files in os.walk(download_directory):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), download_directory))

            # Remove the downloaded music files
            shutil.rmtree(download_directory)

            # Return the zip file for the user to download
            with open(zip_file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename={download_id}.zip'

            # Remove the zip file after the user downloads it
            os.remove(zip_file_path)

            return response

        except subprocess.CalledProcessError as e:
            # Handle subprocess error
            message = f"spotdl command returned non-zero exit status: {e.returncode}"
            return render(request, 'error.html', {'message': message})

        except Exception as e:
            # Handle other exceptions
            message = f"Error: {str(e)}"
            return render(request, 'error.html', {'message': message})

    else:
        return render(request, 'nopage.html')