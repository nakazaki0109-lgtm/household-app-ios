# 実行するたびに取得し直すソース

このスキルの存在理由は「モデルが新しくなるたびに古い記述を削る」ことにある。モデル固有の違いは、`references/timeless-checklist.md` のようにローカルへスナップショットとして固定してはいけない。固定した瞬間からそれ自体が陳腐化するもの(このスキル自身がまさに監査対象になるもの)になるため、**毎回WebFetchで取得し直す。**

## 取得するURL

1. 概要: `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview`
   - 「Prompting best practices」へのリンク先が変わっていないか確認する
2. ベストプラクティス本体(技法一覧の生きたリファレンス): `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices`
   - 冒頭の「Model-specific guidance」表を確認する

## 手順

1. 上記1・2を順にWebFetchで取得する
2. 2の冒頭表から、**今回のセッションを実際に動かしているモデル**(システムプロンプトに書かれているモデル名)に対応する行を探し、そのモデル固有ページのURLを取得する
3. そのモデル固有ページ(例:「Prompting Claude Sonnet 5」)を読み、そのモデルで変わった点・注意点を把握する
4. 2の「General principles」以降の各セクション(Output and formatting / Tool use / Thinking and reasoning / Agentic systems / Capability-specific tips / Migration considerations)を読み、`references/timeless-checklist.md` に載っていない新しい技法や、チェックリストの前提を崩すような変更がないか確認する

## 差分が見つかったら

- 監査対象の文書に対する指摘としてそのまま使う
- あわせて、`references/timeless-checklist.md` 自体の更新も提案する(このスキル自身も監査対象であることを忘れない)。ただしチェックリストの更新も他の文書と同様、提案止まりにしてユーザーの承認を待つ

## 取得できなかった場合

WebFetchが失敗した、あるいはネットワークにアクセスできない環境の場合は、`references/timeless-checklist.md` のみを根拠にレビューを行い、「最新のモデル固有ガイドは未確認」であることを報告の冒頭で明記する。
