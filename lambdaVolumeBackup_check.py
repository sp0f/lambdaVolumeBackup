import boto3

ec2 = boto3.resource('ec2')
retention_days = 2
volume_list=[]

for volume in ec2.volumes.filter(Filters=[{'Name': 'tag:lambdaVolumeBackup', 'Values': ['true']}]):
    if volume.tags:
        result = filter(lambda tag: tag['Key'] == 'lambdaVolumeBackup', volume.tags)
        if len(result) != 0:
            if (result[0]['Value']) == "true":
                volume_snapshots=volume.snapshots.all()
                snapshotCount=0
                for snapshot in volume_snapshots:
                    if snapshot.description.startswith('lambdaVolumeBackup-'):
                        snapshotCount=+1
                if snapshotCount < retention_days:
                    volume_list.append(volume.id+"("+str(snapshotCount)+")")

if len(volume_list) != 0:
    print "CRITICAL backup retention problem (<"+str(retention_days)+") or no backup for volume(s): " + ", ".join(volume_list) + " | " + str(len(volume_list))
    exit(2)
else:
    print "OK | 0"
    exit(0)
