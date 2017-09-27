#!/usr/bin/python2.7

import boto3
import datetime
import pytz

def lambda_handler(event,context):
    ec2 = boto3.resource('ec2')
    retention_days = 2

    for volume in ec2.volumes.filter(Filters=[{'Name': 'tag:lambdaVolumeBackup', 'Values': ['true']}]):
        description = "lambdaVolumeBackup-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + volume.volume_id

        # create snapshot

        snapshot = volume.create_snapshot(volume.volume_id, Description=description)

        if snapshot:
            print "Snapshot: " + str(snapshot.id) + " created successfully"
            snapshot.create_tags(
                Tags=[
                    {
                        'Key': 'archive',
                        'Value': 'true'
                    }
                ]
            )

        for snapshot in volume.snapshots.all():
            '''
            if snapshot.description.startswith('lambdaVolumeBackup-'):
                print snapshot.id
                print str(datetime.datetime.now().replace(tzinfo=None) - snapshot.start_time.replace(tzinfo=None))+" > "\
                    + str(datetime.timedelta(days=retention_days)) + " = " \
                    + str((datetime.datetime.now().replace(tzinfo=None) - snapshot.start_time.replace(tzinfo=None)) > datetime.timedelta(days=retention_days))
            '''
            if snapshot.description.startswith('lambdaVolumeBackup-'):
                if (datetime.datetime.now().replace(tzinfo=None) - snapshot.start_time.replace(
                        tzinfo=None)) > datetime.timedelta(days=retention_days):
                    print("\t\tDeleting snapshot [%s - %s]" % (snapshot.id, snapshot.description))
                    snapshot.delete()
    print("lambdaVolumeBackup completed!")
    return True
