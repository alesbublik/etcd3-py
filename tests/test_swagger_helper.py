import inspect
import json
import os

from etcd3.models import AlarmRequestAlarmAction, etcdserverpbAlarmType
from etcd3.swagger_helper import SwaggerSpec

with open(os.path.join(os.path.dirname(inspect.getfile(SwaggerSpec)), 'rpc.swagger.json')) as f:
    spec = json.load(f)
sh = SwaggerSpec(spec)


def test_swagger_helper():
    assert 'definitions' in dir(sh)
    assert 'post' in dir(sh.paths['/v3alpha/auth/authenticate'])
    assert sh.swagger == spec['swagger']
    assert repr(sh.paths['/v3alpha/auth/authenticate']).startswith('SwaggerPath')
    assert sh.paths['/v3alpha/auth/authenticate']._ref == '#/paths/v3alpha_auth_authenticate'
    assert sh.getPath('/v3alpha/auth/authenticate') == sh.paths['/v3alpha/auth/authenticate']
    assert sh.paths.v3alpha_auth_authenticate.post.parameters[
               0]._ref == '#/paths/v3alpha_auth_authenticate/post/parameters__0'
    # assert sh.ref('#/paths/v3alpha_auth_authenticate/post/parameters__0') == sh.paths.v3alpha_auth_authenticate.post.parameters[0]
    assert sh.paths.v3alpha_auth_authenticate.post.parameters[0].schema == sh.getSchema(
        'etcdserverpbAuthenticateRequest')
    assert sh.ref('#/paths/v3alpha_auth_disable/post/summary') == 'AuthDisable disables authentication.'
    assert sh.ref('#/definitions/etcdserverpbAlarmResponse').properties.alarms.type == 'array'
    assert sh.getSchema('etcdserverpbTxnResponse')._ref == '#/definitions/etcdserverpbTxnResponse'
    etcdserverpbDeleteRangeRequest = sh.getSchema('etcdserverpbDeleteRangeRequest')
    data = {'key': b'foo', 'range_end': b'foz', 'prev_kv': 1}
    encoded = etcdserverpbDeleteRangeRequest.encode(data)
    assert encoded == {'key': 'Zm9v', 'range_end': 'Zm96', 'prev_kv': True}
    decoded = etcdserverpbDeleteRangeRequest.decode(encoded)
    assert decoded == data
    assert sh.definitions._get('etcdserverpbDeleteRangeRequest').encode(data) == encoded

    etcdserverpbAlarmRequest = sh.getSchema('etcdserverpbAlarmRequest')
    data = {}
    encoded = etcdserverpbAlarmRequest.encode(data)
    assert encoded == {'action': 'GET', 'alarm': 'NONE'}
    decoded = etcdserverpbAlarmRequest.decode(encoded)
    assert decoded == {'action': AlarmRequestAlarmAction.GET, 'alarm': etcdserverpbAlarmType.NONE}

    schema = sh.getSchema('etcdserverpbRangeResponse')
    model = schema.getModel()
    data = {
        u'count': u'1',
        u'header': {
            u'raft_term': u'2', u'revision': u'10',
            u'cluster_id': u'11588568905070377092',
            u'member_id': u'128088275939295631'
        },
        u'kvs': [
            {
                u'mod_revision': u'10', u'value': u'YmFy',
                u'create_revision': u'5', u'version': u'6',
                u'key': u'Zm9v'
            }
        ]
    }
    decoded = schema.decode(data)
    modelized = model(decoded)
    assert modelized.count == 1
    assert modelized.header.raft_term == 2
    assert modelized.kvs[0].key == b'foo'
    assert modelized.kvs[0].value == b'bar'

