import React from 'react'
import $ from 'jquery'
import { withRouter } from 'react-router-dom'

import Console from './Console'
import UserPanel from './UserPanel'
import Nav from './Nav'
import Content from './Content'
import ItemPanel from './ItemPanel'
import StatusBar from './StatusBar'
import getTree from './node'
import upload from './upload'
import { headRes, joinPaths, splitBaseName } from './util'
import watch from './watch'
import conf from './conf'
import './css/Explorer.css'

class Explorer extends React.Component {
  state = {
    tree: null,
    uploadPath: null,
  }

  componentWillReceiveProps = async (props) => {
    await this.state.tree.setCurrentPath(props.currentPath);
    this.setState({});
  }

  componentDidMount = async () => {
    window.upload = this.openFileSelection;
    const tree = await getTree(this.props.rootPath);
    await tree.setCurrentPath(this.props.currentPath);
    window.root = tree.root;
    this.setState({tree: tree});
  }

  render() {
    const tree = this.state.tree;
    if (!tree) return null;
    return (
      <div className="explorer">
        <header className="horizontal">
          <div className="left child">
            <Console/>
          </div>
          <div className="right child">
            <a
              id="todo"
              href="/?todo"
              target="_blank"
              rel="noopener noreferrer"
            >
              TODO
            </a>
            <UserPanel/>
          </div>
        </header>
        <main className="horizontal">
          <Nav tree={this.state.tree}
            onNodeClicked={this.onNodeClickedInNav}
            onNodeToggled={this.onNodeToggledInNav}
          />
          <Content
            currentDir={this.state.tree.currentDir}
            currentItem={this.state.tree.currentItem}
            onClick={this.onItemClickedInContent}
            onItemChange={() => this.setState({})}
          />
          <ItemPanel node={tree.currentItem || tree.currentDir}/>
        </main>
        <footer>
          <div className="child">
            <StatusBar item={tree.currentItem || tree.currentDir}/>
          </div>
        </footer>
        <div style={{display: 'none'}}>
          <input id="upload"
            type="file"
            multiple
            style={{display: 'none'}}
            onChange={this.onFileInputChange}
          />
        </div>
      </div>
    );
  }

  onNodeClickedInNav = async (node) => {
    if (node.isCurrentDir()) {
      await node.toggle();
    } else {
      this.changeCurrentDir(node);
    }
    this.setState({});
  }

  onItemClickedInContent = async (node) => {
    if (node && node.isCurrentItem()) {
      if (node.meta.listable) {
        this.changeCurrentDir(node);
      } else {
        const url = conf.api_origin + node.meta.path;
        const a = $(`<a href="${url}" target="_blank" style="display: none">`);
        a.attr('rel', 'noopener noreferer');
        $('body').append(a);
        a[0].click();
        a.remove();
      }
    } else {
      this.state.tree.currentItem = node;
    }
    this.setState({});
  }

  onNodeToggledInNav = () => {
    this.setState({});
  }

  changeCurrentDir = (node) => {
    this.state.tree.setCurrentDir(node);
    this.props.history.push(node.meta.path);
  }

  openFileSelection = (path) => {
    this.setState({
      uploadPath: path || '',
    }, () => $('#upload').click());
  }

  onFileInputChange = async () => {
    let [dirpath, name] = splitBaseName(this.state.uploadPath);
    dirpath = joinPaths(this.getCurrentDirPath(), dirpath);
    const fileInput = $('#upload');
    const files = fileInput[0].files;
    if (files.length === 1) {
      this.doUploadFile(dirpath, name, files[0]);
    } else {
      for (let i = 0; i < files.length; ++i) {
        this.doUploadFile(dirpath, null, files[i]);
      }
    }
    fileInput.val(null);
  }

  getCurrentDirPath = () => {
    return this.state.tree.currentDir.meta.path;
  }

  doUploadFile = (dirpath, name, file) => {
    const path = joinPaths(dirpath, (name || file.name));
    upload(path, file, {
      onHashProgress: this.onHashProgress,
    });
    watch(() => this.watchPath(dirpath, path));
  }

  onHashProgress = (offset, size) => {
    const percent = (offset / size * 100).toFixed(2);
    console.log(percent + '%');
  }

  watchPath = async (dirpath, path) => {
    const res = await headRes(path);
    if (res.status === 200) {
      const dir = await this.state.tree.findByPath(dirpath);
      await dir.update();
      this.setState({});
      return true;
    }
  }
}

Explorer = withRouter(Explorer);

export default Explorer;
