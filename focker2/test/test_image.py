from dataset_test_base import DatasetTestBase
from dataset_cmd_test_base import DatasetCmdTestBase
from focker.core import Image
import focker.yaml as yaml
from focker.__main__ import main
from tempfile import TemporaryDirectory
import os
import stat


class TestImage(DatasetTestBase):
    _meta_class = Image


class TestImageCmd(DatasetCmdTestBase):
    _meta_class = Image

    def test14_build(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump(dict(
                    base='freebsd-latest',
                    steps=[
                        dict(run=[
                            'touch /.focker-unit-test'
                        ])
                    ]
                ), f)
            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image' ]
            main(cmd)
            assert Image.exists_tag('focker-unit-test-image')
            im = Image.from_tag('focker-unit-test-image')
            try:
                assert os.path.exists(os.path.join(im.path, '.focker-unit-test'))
            finally:
                im.destroy()

    def test15_build_with_copy(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'dummyfile'), 'w') as f:
                f.write('focker-unit-test-image-build\n')
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump(dict(
                    base='freebsd-latest',
                    steps=[
                        dict(copy=[
                            [ 'dummyfile', '/etc/dummyfile', { 'chown': '65534:65534', 'chmod': 0o600 } ]
                        ])
                    ]
                ), f)
            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image' ]
            main(cmd)
            assert Image.exists_tag('focker-unit-test-image')
            im = Image.from_tag('focker-unit-test-image')
            try:
                fnam = os.path.join(im.path, 'etc/dummyfile')
                assert os.path.exists(fnam)
                with open(fnam) as f:
                    assert f.read() == 'focker-unit-test-image-build\n'
                st = os.stat(fnam)
                assert stat.S_IMODE(st.st_mode) == 0o600
                assert st.st_uid == 65534
                assert st.st_gid == 65534
            finally:
                im.destroy()
