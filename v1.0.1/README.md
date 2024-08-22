
## git 신규 업로드 방법
#### 해당 프로젝트로 이동후
#### git config --global user.name "Your Name"
#### git config --global user.email "your.email@example.com"
#### git init
#### git branch 새브랜치이름
#### git checkout 새브랜치이름 # 브랜치전환
#### git checkout -b 새브랜치이름 # 새브랜치를 생성하고 바로 이동까지 한번에
#### git remote add origin https://github.com/깃허브계정이름/해당레포지토리.git
#### git pull origin main # main브랜치 가져오기?


## 파일 업로드 방법
#### git checkout 브랜치이름 # 해당 브랜치로 이동
#### git branch # 편집 환경 위치 확인
#### git add 파일명.포맷
#### git commit -m "커밋할 이름"
#### git push origin 브랜치이름

## 파일 추적해제 방법
####  git rm --cached 파일이름.포맷
####  git commit -m "커밋할 이름"
####  git push origin 브랜치이름 

## git clean -df는 사용하지 말것
## git push -f origin main # 강제로 푸시

#### git add 파일명.포맷
#### git commit -m "커밋할 이름"
#### git push origin 브랜치이름

