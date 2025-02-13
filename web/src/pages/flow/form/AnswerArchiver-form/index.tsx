import React, { useState } from 'react';
import { Typography, Spin, Alert, Form, Input, Button } from 'antd';

const { Title, Paragraph } = Typography;

const ApiConfigForm = () => {
    // 初始化状态
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [apiConfig, setApiConfig] = useState({
        external_api_host: "",
        external_api_path: "",
        authorization: "",
        appId: "",
        formId: ""
    });

    // 表单提交处理函数
    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(apiConfig),
            });

            if (response.ok) {
                const resultData = await response.json();
                setResult(resultData.message || "配置成功！");
            } else {
                const errorMsg = await response.text();
                setError(`提交失败，HTTP状态码：${response.status} - ${errorMsg}`);
            }
        } catch (error) {
            setError('提交过程中发生网络错误，请稍后再试。');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <Title level={2}>配置轻魔方API参数</Title>
            <Paragraph>请填写以下API参数：</Paragraph>

            <Form onSubmit={handleSubmit}>
                <Form.Item label="域名">
                    <Input
                        value={apiConfig.external_api_host}
                        onChange={(e) => setApiConfig({ ...apiConfig, external_api_host: e.target.value })}
                    />
                </Form.Item>
                <Form.Item label="路径">
                    <Input
                        value={apiConfig.external_api_path}
                        onChange={(e) => setApiConfig({ ...apiConfig, external_api_path: e.target.value })}
                    />
                </Form.Item>
                <Form.Item label="Token">
                    <Input
                        value={apiConfig.authorization}
                        onChange={(e) => setApiConfig({ ...apiConfig, authorization: e.target.value })}
                    />
                </Form.Item>
                <Form.Item label="应用ID">
                    <Input
                        value={apiConfig.appId}
                        onChange={(e) => setApiConfig({ ...apiConfig, appId: e.target.value })}
                    />
                </Form.Item>
                <Form.Item label="表单ID">
                    <Input
                        value={apiConfig.formId}
                        onChange={(e) => setApiConfig({ ...apiConfig, formId: e.target.value })}
                    />
                </Form.Item>
                <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading}>
                        提交
                    </Button>
                </Form.Item>
            </Form>

            {loading && (
                <div style={{ textAlign: 'center', margin: '20px 0' }}>
                    <Spin size="large" tip="处理中..." />
                </div>
            )}
            {error && (
                <Alert
                    message="错误"
                    description={error}
                    type="error"
                    showIcon
                    style={{ marginBottom: '20px' }}
                />
            )}
            {result && (
                <div>
                    <Title level={3}>结果:</Title>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default ApiConfigForm;