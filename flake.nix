{
  description = "Apple Music decryption tool";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};

      # grpcioのwheelがlibstdc++を必要とするためstdenv.cc.cc.libを追加
      # ローカルwrapper-manager用にQEMUも追加
      runtimeDeps = [ pkgs.poetry pkgs.ffmpeg pkgs.gpac pkgs.bento4 pkgs.stdenv.cc.cc.lib pkgs.qemu ];

      runScript = pkgs.writeShellApplication {
        name = "apple-music-decrypt";
        runtimeInputs = runtimeDeps;
        text = ''
          # pyproject.tomlを含むリポジトリを探す
          if [ -f "$PWD/pyproject.toml" ]; then
            REPO="$PWD"
          else
            REPO="${self}"
          fi

          # config.tomlがなければサンプルからコピー(カレントディレクトリに)
          if [ ! -f "$PWD/config.toml" ]; then
            cp "$REPO/config.example.toml" "$PWD/config.toml"
            echo "config.toml を $PWD に作成しました。"
            echo "  [instance] セクションのwrapper-manager URLを設定してから再実行してください。"
            echo "  公開インスタンス例: url = \"wm.wol.moe\" / secure = true"
            exit 0
          fi

          # 仮想環境が未インストールなら初回セットアップ
          if ! poetry --directory="$REPO" env info --path &>/dev/null; then
            echo "Python依存関係をインストール中(初回のみ)..."
            poetry --directory="$REPO" install --only main
          fi

          # grpcioのwheelはlibstdc++.so.6を必要とする
          export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
          exec poetry --directory="$REPO" run python "$REPO/main.py" "$@"
        '';
      };
    in
    {
      packages.${system}.default = runScript;

      apps.${system}.default = {
        type = "app";
        program = "${runScript}/bin/apple-music-decrypt";
      };

      devShells.${system}.default = pkgs.mkShell {
        packages = runtimeDeps;
        shellHook = ''
          # grpcioのwheelはlibstdc++.so.6を必要とする
          export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

          # 依存関係が未インストールなら自動セットアップ
          if ! poetry env info --path &>/dev/null 2>&1; then
            echo "Python依存関係をインストール中..."
            poetry install --only main
          fi
          echo "AppleMusicDecrypt 環境 (poetry run python main.py で起動)"
        '';
      };
    };
}
