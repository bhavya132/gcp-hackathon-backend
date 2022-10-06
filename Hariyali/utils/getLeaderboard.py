from sqlalchemy.orm import Session
from Hariyali.Database import models, SessionLocal
import json


def getLeaderboard(db: Session):
    allUserInfo = db.query(models.User).all()
    leaderboard = [[user.name,user.email, user.score] for user in allUserInfo]

    leaderboard.sort(key=lambda x:x[2], reverse=True)
    print(leaderboard)
    # leaderboardResponse = dict(zip([i for i in range(1,len(leaderboard)+1)],[{"userEmail":x[0], "score":x[1]} for x in leaderboard]))
    leaderboardResponse = dict(zip([i for i in range(1,len(leaderboard)+1)],[[x[0],x[1], x[2]] for x in leaderboard]))
    return json.dumps(leaderboardResponse)

if __name__ == '__main__':
    print(getLeaderboard(SessionLocal()))