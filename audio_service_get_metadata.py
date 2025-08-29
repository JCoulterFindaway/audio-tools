

from audio_service_client import AudioServiceClient

client = AudioServiceClient(
    url='https://audio-service.findaway.com',
)

content_id = '1295843'

cohort = client.get_cohort(
    content_id=content_id
)

print(cohort)


durations = {}
for file in cohort['fileList']:

    check_sum = file['checksum']

    metadata = client.get_audio_metadata(check_sum)

    durations[check_sum] = metadata['duration']
    print(metadata['duration'])


print(durations)


