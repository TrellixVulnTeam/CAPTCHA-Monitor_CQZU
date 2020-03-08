from argparse import ArgumentParser
from tbselenium.tbdriver import TorBrowserDriver
import tbselenium.common as cm
from tbselenium.utils import launch_tbb_tor_with_stem


def launch_tb_with_stem(tbb_dir):
    tor_process = launch_tbb_tor_with_stem(tbb_path=tbb_dir)
    with TorBrowserDriver(tbb_dir,
                          tor_cfg=cm.USE_STEM) as driver:
        driver.load_url("https://check.torproject.org", wait_on_page=3)
        print(driver.find_element_by("h1.on").text)
        print(driver.find_element_by(".content > p").text)

    tor_process.kill()


def main():
    desc = "Use TorBrowserDriver with Stem"
    tbb_path = "/home/woswos/Desktop/tor-browser_en-US/"
    launch_tb_with_stem(tbb_path)


if __name__ == '__main__':
    main()
