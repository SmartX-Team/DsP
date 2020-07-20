from tower.dsp_tower import DsPTower
import datetime


def do_epoch(mode: str) -> float:
    tstart = datetime.datetime.now()

    dsp_inst = DsPTower()
    dsp_inst.start(mode)

    tend = datetime.datetime.now()
    elasped_time = tend - tstart

    return elasped_time.total_seconds()


def main():
    # epoch = 1
    # sleep_time = 0

    # prov_times = list()
    # release_times = list()
    #
    # for i in range(0, epoch):
    #     prov_time = do_epoch("provisioning")
    #     logging.info("Total Elasped Time for {}: {}".format(prov_time, "provisioning"))
    #     prov_times.append(prov_time)
    #     time.sleep(sleep_time)
    #
    #     release_time = do_epoch("release")
    #     logging.info("Total Elasped Time for {}: {}".format(prov_time, "provisioning"))
    #     release_times.append(release_time)
    #     time.sleep(sleep_time)
    #
    # logging.info("Elasped Time for Provisioning")
    # logging.info(prov_times)
    #
    # logging.info("Elasped Time for Release")
    # logging.info(release_times)

    prov_time = do_epoch("provisioning")
