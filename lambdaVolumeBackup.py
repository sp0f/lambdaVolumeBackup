#!/usr/bin/python2.7

import boto3
import datetime
import pytz

def lambda_handler(event,context):
    ec2 = boto3.resource('ec2')
    retention_days = 2

    instances = ec2.instances.filter(Filters=[
        {
            'Name': 'instance-state-name',
            'Values': ['running']
        }
    ])

    for instance in instances:
        # print filter(lambda tag: tag['Key'] == 'Name', instance.tags)
        instance_name = filter(lambda tag: tag['Key'] == 'Name', instance.tags)[0]['Value']

        for volume in ec2.volumes.filter(Filters=[{'Name': 'attachment.instance-id', 'Values': [instance.id]}]):
            if volume.tags:
                result = filter(lambda tag: tag['Key'] == 'lambdaVolumeBackup', volume.tags)
                if len(result) != 0:
                    if (result[0]['Value']) == "true":
                        description = "lambdaVolumeBackup-" + datetime.datetime.now().strftime(
                            "%Y%m%d-%H%M%S") + "-" + instance_name + "-" + volume.volume_id

                        # create snapshot

                        snapshot = volume.create_snapshot(volume.volume_id, Description=description)

                        if snapshot:
                            print "Snapshot: " + str(snapshot.id) + " created sucessfully"
                            snapshot.create_tags(
                                Tags=[
                                    {
                                        'Key': 'archive',
                                        'Value': 'true'
                                    }
                                ]
                            )

                        # retention
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
