
import json

from audio_service_client import AudioServiceClient

client = AudioServiceClient(
    url='https://audio-service.findaway.com',
)

# content_id = '1330752' # https://gateway.audioengine.io/title-management/1330752/audio
content_id = '1298537' # https://gateway.audioengine.io/title-management/1298537/audio

# fetch the cohort
cohort = client.get_cohort(
    content_id=content_id
)

# remove the playList and the versionId(so it will get a new one)
cohort.pop('playList')
cohort.pop('versionId')

print(
    client.post_cohort(
        content_id=content_id,
        cohort=json.dumps(cohort)
    )
)
