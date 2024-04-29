from unittest.mock import call
from unittest.mock import patch

import requests
from common import setup_hosted_zone_with_alias

from manual_scans.aws.aws_alias_s3 import main


@patch("manual_scans.aws.aws_alias_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_detects_vulnerable_domains(arg_parse_mock, print_list_mock, moto_route53, moto_cloudfront, requests_mock):

    setup_hosted_zone_with_alias(moto_route53, "dns_mock.s3-website.amazonaws.com")

    requests_mock.get("http://vulnerable.domain-protect.com.", status_code=404, text="Code: NoSuchBucket")

    main()

    expected_vulnerable_call = call(["vulnerable.domain-protect.com."], "INSECURE_WS")
    expected_missing_call = call(["vulnerable.domain-protect.com.dns_mock.s3-website.amazonaws.com"], "OUTPUT_WS")
    print_list_mock.assert_has_calls([expected_vulnerable_call, expected_missing_call])


@patch("manual_scans.aws.aws_alias_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_ignores_non_vulnerable_domains(arg_parse_mock, print_list_mock, moto_route53, requests_mock):
    setup_hosted_zone_with_alias(moto_route53, "dns_mock.s3-website.amazonaws.com")

    requests_mock.get("http://vulnerable.domain-protect.com.", status_code=200, text="All good here")

    main()

    print_list_mock.assert_not_called()


@patch("manual_scans.aws.aws_alias_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_ignores_non_s3_domains(arg_parse_mock, print_list_mock, moto_route53, requests_mock):
    setup_hosted_zone_with_alias(moto_route53, "dns_mock.blah.amazonaws.com")

    requests_mock.get("http://vulnerable.domain-protect.com.", status_code=404, text="Code: NoSuchBucket")

    main()

    print_list_mock.assert_not_called()


@patch("manual_scans.aws.aws_alias_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_ignores_domains_with_connection_error(arg_parse_mock, print_list_mock, moto_route53, requests_mock):
    setup_hosted_zone_with_alias(moto_route53, "dns_mock.s3-website.amazonaws.com")

    requests_mock.get("http://vulnerable.domain-protect.com.", exc=requests.exceptions.ConnectionError)

    main()

    print_list_mock.assert_not_called()
