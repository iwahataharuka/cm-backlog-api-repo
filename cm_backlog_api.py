import requests
from typing import Dict, Tuple


class CMBacklogAPI:
    """
    Backlog APIのCodeMonkey用wrapperクラス
    現段階では課題の作成のみ対応
    """
    def __init__(self, api_key: str) -> None:
        """コンストラクタ
        """
        self.SERVER_URL: str = 'https://n-contents.backlog.com/api/v2'
        self.API_KEY: str = api_key

    def _get(self, path: str, params: Dict = dict(), **kwargs) -> requests.Response:
        """BacklogAPIにgetする内部関数

        Args:
            path (str): getするエンドポイントのパス
            params (:obj:`dict`, optional): 送信する情報. Defaults to empty dict.

        Returns:
            response (requests.Response): APIのレスポンス
        """
        params['apiKey'] = self.API_KEY
        url = self.SERVER_URL + path

        return requests.get(url=url, params=params, **kwargs)

    def _post(self, path: str, params: Dict = dict(), **kwargs) -> requests.Response:
        """BacklogAPIにpostする内部関数

        Args:
            path (str): postするエンドポイントのパス
            params (:obj:`dict`, optional): 送信する情報. Defaults to empty dict.

        Returns:
            response (requests.Response): APIのレスポンス
        """
        params['apiKey'] = self.API_KEY
        url = self.SERVER_URL + path

        return requests.post(url=url, params=params, **kwargs)

    def create_issue(
        self,
        project_id: int,
        summary: str,
        issue_type_id: int,
        description: str = '',
        **kwargs,
    ) -> Tuple[bool, str, requests.Response]:
        """新しい課題を追加します。
        See: https://developer.nulab.com/ja/docs/backlog/api/2/add-issue/

        Args:
            project_id (int): 課題を登録するプロジェクトのID
            summary (str): 	課題の件名
            issue_type_id (int): 課題の種別のID
            description (str, optional): 課題の詳細. Defaults to empty.
            **kwargs: その他のパラメータ (camelCase)

        Returns:
            is_success (bool): 成功したかどうか
            url (str): 登録した課題のURL
            response (requests.Response): APIのレスポンス
        """
        # priorityIdは必須なので、指定の無い場合デフォルト値を設定
        if 'priorityId' not in kwargs:
            try:
                res = self._get('/priorities')
                res_json = res.json()
                for priority in res_json:
                    if priority['name'] == '中':
                        kwargs['priorityId'] = priority['id']
                        break
                else:
                    kwargs['priorityId'] = res_json[0]['id']
            except Exception:
                kwargs['priorityId'] = 3  # 中

        params = {
            'projectId': project_id,
            'summary': summary,
            'issueTypeId': issue_type_id,
            'description': description,
            **kwargs,
        }
        response = self._post('/issues', params=params)
        if response.status_code == 201:
            try:
                issue_key = response.json()['issueKey']
                url = f'https://n-contents.backlog.com/view/{issue_key}'
                return True, url, response
            except requests.exceptions.JSONDecodeError:
                return False, '', response
        else:
            return False, '', response
